package org.cms.jpos.dao;

import org.cms.jpos.config.DBConnectionManager;

import java.sql.Connection;
import java.sql.PreparedStatement;

public class TransactionDAO {

    public static void saveTransaction(
            String mti,
            String panMasked,
            String amount,
            String stan,
            String terminal,
            String merchant,
            String response
    ) {

        String sql = "INSERT INTO CMS_TRANSACTIONS " +
                "(MTI, PAN_MASKED, AMOUNT, STAN, TERMINAL_ID, MERCHANT_ID, RESPONSE_CODE) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = DBConnectionManager.getDataSource().getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, mti);
            ps.setString(2, panMasked);
            ps.setString(3, amount);
            ps.setString(4, stan);
            ps.setString(5, terminal);
            ps.setString(6, merchant);
            ps.setString(7, response);

            ps.executeUpdate();

            System.out.println("✅ Transaction saved");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}