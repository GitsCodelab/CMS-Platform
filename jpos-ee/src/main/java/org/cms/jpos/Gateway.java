package org.cms.jpos;

import java.io.DataInputStream;
import java.io.EOFException;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Level;
import java.util.logging.Logger;

public class Gateway {
    private static final Logger logger = Logger.getLogger(Gateway.class.getName());
    private static final AppConfig CONFIG = AppConfig.load();
    private static volatile boolean running = true;

    // public static void main(String[] args) {
    //     logger.info(String.format(
    //         "Starting CMS Gateway port=%d timeoutMs=%d maxMessageLength=%d maxClients=%d requireMac=%s",
    //         CONFIG.port,
    //         CONFIG.socketTimeoutMs,
    //         CONFIG.maxMessageLength,
    //         CONFIG.maxClients,
    //         CONFIG.requireMac
    //     ));


     public static void main(String[] args) {
        logger.info(String.format(
            "Starting CMS Gateway port=%d timeoutMs=%d maxMessageLength=%d maxClients=%d requireMac=%s",
            CONFIG.port,
            CONFIG.socketTimeoutMs,
            CONFIG.maxMessageLength,
            CONFIG.maxClients,
            CONFIG.requireMac
        ));


        ExecutorService executor = Executors.newFixedThreadPool(CONFIG.maxClients);
        try (ServerSocket serverSocket = new ServerSocket(CONFIG.port)) {
            while (running) {
                Socket clientSocket = serverSocket.accept();
                executor.submit(() -> handleClient(clientSocket));
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Startup error", e);
        } finally {
            executor.shutdownNow();
        }
    }

    private static void handleClient(Socket clientSocket) {
        try (Socket socket = clientSocket) {
            socket.setSoTimeout(CONFIG.socketTimeoutMs);
            DataInputStream in = new DataInputStream(socket.getInputStream());
            OutputStream out = socket.getOutputStream();

            while (true) {
                byte[] lenBuf = new byte[2];
                try {
                    in.readFully(lenBuf);
                } catch (EOFException eof) {
                    break;
                }

                int length = ((lenBuf[0] & 0xFF) << 8) | (lenBuf[1] & 0xFF);
                if (length <= 5 || length > CONFIG.maxMessageLength) {
                    logger.warning("Rejected connection due to invalid message length=" + length);
                    break;
                }

                byte[] msg = new byte[length];
                in.readFully(msg);

                byte[] response = ISOMessageHandler.processRawMessage(msg, length);
                if (response != null) {
                    byte[] resp = new byte[response.length + 2];
                    resp[0] = (byte) (response.length >> 8);
                    resp[1] = (byte) response.length;
                    System.arraycopy(response, 0, resp, 2, response.length);
                    out.write(resp);
                    out.flush();
                }
            }
        } catch (SocketTimeoutException e) {
            logger.info("Client socket timed out");
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Client error", e);
        }
    }
}
