"""
single_instance.py - Single Instance Application Manager

Purpose:
    Ensures only one instance of the application runs at a time using Qt's
    QLocalServer/QLocalSocket IPC mechanism. When a second instance is launched,
    it signals the first instance to show its window and then exits.
    
    Features:
    - QLocalServer-based single instance detection
    - IPC communication to activate existing window
    - Stale server cleanup on crashes
    - Zero external dependencies (Qt-only)
    - Clean integration with system tray behavior

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional, Callable
import sys


class SingleInstanceManager(QObject):
    """
    Manages single-instance behavior for the application.
    
    Uses QLocalServer to create a named server that only one instance
    can successfully start. Secondary instances connect as clients to
    send activation commands.
    
    Signals:
        activate_window: Emitted when a secondary instance requests activation
    """
    
    # Signal emitted when secondary instance wants to activate the main window
    activate_window = pyqtSignal()
    
    # Unique server name for this application
    SERVER_NAME = "MasterRefreshingAppInstance_2024"
    
    # Command sent by secondary instances
    COMMAND_SHOW = b"SHOW"
    
    def __init__(self):
        """Initialize the single instance manager."""
        super().__init__()
        self.server: Optional[QLocalServer] = None
        self.is_primary = False
    
    def try_start_as_primary(self) -> bool:
        """
        Attempt to start as the primary (first) instance.
        
        Returns:
            True if this is the primary instance (server started successfully)
            False if another instance is already running
        """
        # Try to create and start the local server
        self.server = QLocalServer(self)
        
        # First, try to listen
        if not self.server.listen(self.SERVER_NAME):
            # Failed to listen - might be stale server or real instance
            # Try to remove potentially stale server and retry
            QLocalServer.removeServer(self.SERVER_NAME)
            
            # Try listening again after cleanup
            if not self.server.listen(self.SERVER_NAME):
                # Still failed - a real instance must be running
                self.server.deleteLater()
                self.server = None
                return False
        
        # Successfully listening - we are the primary instance
        self.is_primary = True
        
        # Connect the signal for incoming connections
        self.server.newConnection.connect(self._handle_new_connection)
        
        return True
    
    def _handle_new_connection(self):
        """Handle incoming connection from a secondary instance."""
        if not self.server:
            return
        
        # Get the incoming socket
        socket = self.server.nextPendingConnection()
        if not socket:
            return
        
        # Wait for data to be available (with timeout)
        if socket.waitForReadyRead(1000):  # 1 second timeout
            # Read the command
            data = socket.readAll()
            # Convert QByteArray to bytes properly
            command = data.data().strip()
            
            # If it's the SHOW command, emit signal to activate window
            if command == self.COMMAND_SHOW:
                self.activate_window.emit()
        
        # Close and clean up the socket
        socket.disconnectFromServer()
        socket.deleteLater()
    
    def signal_existing_instance(self) -> bool:
        """
        Connect to an existing instance and send activation command.
        Called by secondary instances to activate the primary.
        
        Returns:
            True if successfully sent signal to existing instance
            False if connection failed
        """
        socket = QLocalSocket()
        socket.connectToServer(self.SERVER_NAME)
        
        # Wait for connection (2 second timeout)
        if not socket.waitForConnected(2000):
            socket.deleteLater()
            return False
        
        # Send the SHOW command
        socket.write(self.COMMAND_SHOW)
        socket.flush()
        
        # Wait for write to complete
        socket.waitForBytesWritten(1000)
        
        # Disconnect and clean up
        socket.disconnectFromServer()
        if socket.state() != QLocalSocket.LocalSocketState.UnconnectedState:
            socket.waitForDisconnected(1000)
        
        socket.deleteLater()
        return True
    
    def is_primary_instance(self) -> bool:
        """
        Check if this is the primary instance.
        
        Returns:
            True if primary, False otherwise
        """
        return self.is_primary
    
    def cleanup(self):
        """Clean up server resources on shutdown."""
        if self.server:
            self.server.close()
            QLocalServer.removeServer(self.SERVER_NAME)
            self.server.deleteLater()
            self.server = None
