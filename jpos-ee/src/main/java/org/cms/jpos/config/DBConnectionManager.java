package org.cms.jpos.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import javax.sql.DataSource;

public class DBConnectionManager {

    private static final HikariDataSource dataSource;

    static {
        HikariConfig config = new HikariConfig();

        // 🔴 Oracle DB Config (your setup)
        config.setJdbcUrl("jdbc:oracle:thin:@localhost:1521/XEPDB1");
        config.setUsername("system");
        config.setPassword("oracle");

        // 🔴 Oracle Driver
        config.setDriverClassName("oracle.jdbc.OracleDriver");

        // 🔥 Pool settings (optimized for ATM traffic)
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(2);
        config.setIdleTimeout(30000);
        config.setConnectionTimeout(30000);
        config.setMaxLifetime(1800000);

        // Optional performance tuning
        config.setPoolName("CMS-HikariPool");

        dataSource = new HikariDataSource(config);
    }

    public static DataSource getDataSource() {
        return dataSource;
    }
}