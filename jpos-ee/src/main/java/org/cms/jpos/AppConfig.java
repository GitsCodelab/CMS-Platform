package org.cms.jpos;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public final class AppConfig {
    public final int port;
    public final int socketTimeoutMs;
    public final int maxMessageLength;
    public final int maxClients;
    public final int replayWindowSeconds;
    public final boolean requireMac;
    public final boolean requireTls;
    public final List<byte[]> bdkKeys;
    public final List<byte[]> macKeys;

    private AppConfig(
        int port,
        int socketTimeoutMs,
        int maxMessageLength,
        int maxClients,
        int replayWindowSeconds,
        boolean requireMac,
        boolean requireTls,
        List<byte[]> bdkKeys,
        List<byte[]> macKeys
    ) {
        this.port = port;
        this.socketTimeoutMs = socketTimeoutMs;
        this.maxMessageLength = maxMessageLength;
        this.maxClients = maxClients;
        this.replayWindowSeconds = replayWindowSeconds;
        this.requireMac = requireMac;
        this.requireTls = requireTls;
        this.bdkKeys = Collections.unmodifiableList(bdkKeys);
        this.macKeys = Collections.unmodifiableList(macKeys);
    }

    public static AppConfig load() {
        int port = getInt("JPOS_PORT", 8583);
        int socketTimeoutMs = getInt("JPOS_SOCKET_TIMEOUT_MS", 5000);
        int maxMessageLength = getInt("JPOS_MAX_MESSAGE_LENGTH", 4096);
        int maxClients = getInt("JPOS_MAX_CLIENTS", 32);
        int replayWindowSeconds = getInt("JPOS_REPLAY_WINDOW_SECONDS", 300);
        boolean requireMac = getBoolean("JPOS_REQUIRE_MAC", true);
        boolean requireTls = getBoolean("JPOS_REQUIRE_TLS", false);

        if (requireTls) {
            throw new IllegalStateException("TLS is required by config but not implemented in this gateway yet.");
        }

        List<byte[]> bdkKeys = loadKeyList("JPOS_BDK_HEX", "JPOS_BDK_PREVIOUS_HEX");
        List<byte[]> macKeys = loadKeyList("JPOS_MAC_KEY_HEX", "JPOS_MAC_KEY_PREVIOUS_HEX");

        return new AppConfig(
            port,
            socketTimeoutMs,
            maxMessageLength,
            maxClients,
            replayWindowSeconds,
            requireMac,
            requireTls,
            bdkKeys,
            macKeys
        );
    }

    // ✅ FIXED: CLEAN INPUT BEFORE PARSING
    private static List<byte[]> loadKeyList(String primaryName, String previousName) {
        List<byte[]> keys = new ArrayList<>();

        String primary = requireEnv(primaryName);
        String cleanedPrimary = cleanHex(primary);
        keys.add(hexToBytes(cleanedPrimary));

        String previous = System.getenv(previousName);
        if (previous != null && !previous.trim().isEmpty()) {
            String cleanedPrev = cleanHex(previous);
            keys.add(hexToBytes(cleanedPrev));
        }

        return keys;
    }

    private static int getInt(String name, int defaultValue) {
        String value = System.getenv(name);
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        return Integer.parseInt(value.trim());
    }

    private static boolean getBoolean(String name, boolean defaultValue) {
        String value = System.getenv(name);
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        return Boolean.parseBoolean(value.trim());
    }

    private static String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalStateException("Missing required environment variable: " + name);
        }
        return value.trim();
    }

    // ✅ NEW: CLEAN HEX INPUT SAFELY
    private static String cleanHex(String hex) {
        return hex.trim().replaceAll("[^0-9A-Fa-f]", "");
    }

    // ✅ SAFE HEX PARSER
    private static byte[] hexToBytes(String hex) {
        if (hex == null || hex.isEmpty()) {
            throw new IllegalArgumentException("Key is empty");
        }

        if (hex.length() % 2 != 0) {
            throw new IllegalArgumentException("Invalid hex length: " + hex.length());
        }

        byte[] result = new byte[hex.length() / 2];

        for (int i = 0; i < hex.length(); i += 2) {
            result[i / 2] = (byte) Integer.parseInt(hex.substring(i, i + 2), 16);
        }

        return result;
    }
}   