FROM wso2/wso2am:4.3.0

USER root

# Add PostgreSQL driver (مرة واحدة بس)
COPY postgresql-42.5.0.jar \
/home/wso2carbon/wso2am-4.3.0/repository/components/lib/

# Copy config
COPY deployment.toml \
/home/wso2carbon/wso2am-4.3.0/repository/conf/deployment.toml

USER wso2carbon

EXPOSE 8280 8243 9443 9611

CMD ["/home/wso2carbon/wso2am-4.3.0/bin/api-manager.sh"]