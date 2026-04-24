package org.cms.jpos;

import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * jPOS-EE Main Gateway Application
 * Listens on port 8583 for ISO 8583 messages
 */
public class Gateway {
    private static final Logger logger = Logger.getLogger(Gateway.class.getName());
    private static final int PORT = 8583;
    private static volatile boolean running = true;

    public static void main(String[] args) {
        logger.info("Starting CMS jPOS-EE Gateway on port " + PORT);

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            logger.info("Gateway listening on port " + PORT);

            // Accept client connections
            while (running) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    logger.info("Client connected: " + clientSocket.getInetAddress());

                    // Handle client in a thread
                    new Thread(() -> handleClient(clientSocket)).start();
                } catch (Exception e) {
                    logger.log(Level.SEVERE, "Error accepting client", e);
                }
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Failed to start gateway", e);
            System.exit(1);
        }
    }

    /**
     * Handle incoming client connection and ISO messages
     */
    private static void handleClient(Socket clientSocket) {
        try {
            InputStream in = clientSocket.getInputStream();
            OutputStream out = clientSocket.getOutputStream();

            logger.info("Handling client: " + clientSocket.getInetAddress());

            // Read messages and process through ISOMessageHandler
            byte[] buffer = new byte[4096];
            int bytesRead;

            while ((bytesRead = in.read(buffer)) != -1) {
                logger.info("Received " + bytesRead + " bytes from client");

                try {
                    // Process message through handler
                    byte[] response = ISOMessageHandler.processRawMessage(buffer, bytesRead);
                    
                    if (response != null && response.length > 0) {
                        out.write(response);
                        out.flush();
                        logger.info("Response sent to client (" + response.length + " bytes)");
                    }
                } catch (Exception e) {
                    logger.log(Level.SEVERE, "Error processing message", e);
                    // Send error response
                    String errorResp = "ERROR: " + e.getMessage();
                    out.write(errorResp.getBytes());
                    out.flush();
                }
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error handling client", e);
        } finally {
            try {
                clientSocket.close();
                logger.info("Client disconnected");
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Error closing client socket", e);
            }
        }
    }
}

