FROM wso2/wso2is:7.0.0

# Copy configuration files
COPY ./conf/carbon.xml /home/wso2carbon/wso2is-7.0.0/repository/conf/carbon.xml

# Expose ports
EXPOSE 4443 9443 8280 8243

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -k -f https://localhost:9443/api/identity/auth/v1.0/token || exit 1

# Start WSO2 IS
CMD ["/home/wso2carbon/wso2is-7.0.0/bin/wso2server.sh"]
