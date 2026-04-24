package org.cms.jpos;

import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.logging.Logger;
import java.util.logging.Level;

public class Gateway {
    private static final Logger logger = Logger.getLogger(Gateway.class.getName());
    private static final int PORT = 8583;
    private static volatile boolean running = true;

    public static void main(String[] args) {
        logger.info("Starting CMS Gateway on port " + PORT);

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (running) {
                Socket clientSocket = serverSocket.accept();
                new Thread(() -> handleClient(clientSocket)).start();
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Startup error", e);
        }
    }

    private static void handleClient(Socket clientSocket) {
        try {
            InputStream in = clientSocket.getInputStream();
            OutputStream out = clientSocket.getOutputStream();

            while (true) {

                // 🔴 READ LENGTH
                byte[] lenBuf = new byte[2];
                if (in.read(lenBuf) < 2) break;

                int length = ((lenBuf[0] & 0xFF) << 8) | (lenBuf[1] & 0xFF);

                byte[] msg = new byte[length];
                int read = 0;

                while (read < length) {
                    int r = in.read(msg, read, length - read);
                    if (r == -1) break;
                    read += r;
                }

                byte[] response = ISOMessageHandler.processRawMessage(msg, length);

                if (response != null) {
                    byte[] resp = new byte[response.length + 2];
                    resp[0] = (byte) (response.length >> 8);
                    resp[1] = (byte) (response.length);
                    System.arraycopy(response, 0, resp, 2, response.length);

                    out.write(resp);
                    out.flush();
                }
            }

        } catch (Exception e) {
            logger.log(Level.SEVERE, "Client error", e);
        }
    }
}