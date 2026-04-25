package org.cms.jpos.dao;

import org.cms.jpos.config.DBConnectionManager;

import java.sql.Connection;
import java.sql.PreparedStatement;

public class IsoLogDAO {

    public static void saveLog(String request, String response) {

        String sql = "INSERT INTO CMS_ISO_LOG (REQUEST_DUMP, RESPONSE_DUMP) VALUES (?, ?)";

        try (Connection conn = DBConnectionManager.getDataSource().getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, request);
            ps.setString(2, response);

            ps.executeUpdate();

            System.out.println("✅ ISO log saved");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}