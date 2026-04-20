FROM eclipse-temurin:17-jdk-jammy

WORKDIR /opt/jposee

# Copy all available files from build context (includes local binaries, config, deploy)
COPY . /opt/jposee/

# Create necessary directory structure
RUN mkdir -p /opt/jposee/dist/lib && \
    mkdir -p /opt/jposee/dist/deploy && \
    mkdir -p /opt/jposee/dist/config && \
    mkdir -p /opt/jposee/dist/log && \
    if [ -d /opt/jposee/deploy ]; then cp -r /opt/jposee/deploy/* /opt/jposee/dist/deploy/ 2>/dev/null || true; fi && \
    if [ -d /opt/jposee/config ]; then cp -r /opt/jposee/config/* /opt/jposee/dist/config/ 2>/dev/null || true; fi && \
    if [ -d /opt/jposee/lib ]; then cp -r /opt/jposee/lib/* /opt/jposee/dist/lib/ 2>/dev/null || true; fi && \
    chmod -R 755 /opt/jposee/dist && \
    chmod -R 777 /opt/jposee/dist/log

# If no jPOS EE JARs found locally, download base jPOS + dependencies
# Note: jPOS EE requires enterprise credentials - provide your own binaries
RUN if [ ! -f /opt/jposee/dist/lib/jpos-ee-*.jar ] && [ ! -f /opt/jposee/dist/lib/jposee-*.jar ]; then \
      echo "jPOS EE binaries not found in local build context"; \
      echo "To use jPOS EE, provide:"; \
      echo "  1. jPOS EE distribution JAR in lib/ folder"; \
      echo "  2. Enterprise configuration in config/ folder"; \
      echo "  3. Custom deployments in deploy/ folder"; \
      echo "Falling back to base jPOS for development..."; \
      cd /opt/jposee/dist/lib && \
      curl -s -L -o jpos-2.1.8.jar https://repo1.maven.org/maven2/org/jpos/jpos/2.1.8/jpos-2.1.8.jar && \
      curl -s -L -o commons-cli-1.5.0.jar https://repo1.maven.org/maven2/commons-cli/commons-cli/1.5.0/commons-cli-1.5.0.jar && \
      curl -s -L -o jdom2-2.0.6.jar https://repo1.maven.org/maven2/org/jdom/jdom2/2.0.6/jdom2-2.0.6.jar && \
      curl -s -L -o log4j-api-2.17.1.jar https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-api/2.17.1/log4j-api-2.17.1.jar && \
      curl -s -L -o log4j-core-2.17.1.jar https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.17.1/log4j-core-2.17.1.jar && \
      curl -s -L -o log4j-slf4j-impl-2.17.1.jar https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-slf4j-impl/2.17.1/log4j-slf4j-impl-2.17.1.jar && \
      curl -s -L -o slf4j-api-1.7.36.jar https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar && \
      curl -s -L -o org.osgi.core-6.0.0.jar https://repo1.maven.org/maven2/org/osgi/org.osgi.core/6.0.0/org.osgi.core-6.0.0.jar && \
      curl -s -L -o org.osgi.compendium-5.0.0.jar https://repo1.maven.org/maven2/org/osgi/org.osgi.compendium/5.0.0/org.osgi.compendium-5.0.0.jar && \
      curl -s -L -o org.apache.felix.framework-5.6.14.jar https://repo1.maven.org/maven2/org/apache/felix/org.apache.felix.framework/5.6.14/org.apache.felix.framework-5.6.14.jar && \
      curl -s -L -o snakeyaml-2.0.jar https://repo1.maven.org/maven2/org/yaml/snakeyaml/2.0/snakeyaml-2.0.jar && \
      curl -s -L -o commons-lang3-3.12.0.jar https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0.jar && \
      curl -s -L -o commons-codec-1.15.jar https://repo1.maven.org/maven2/commons-codec/commons-codec/1.15/commons-codec-1.15.jar 2>/dev/null || echo "Some dependencies skipped"; \
    else \
      echo "jPOS EE binaries detected in dist/lib"; \
    fi && \
    echo "jPOS EE setup complete" && \
    ls -lah /opt/jposee/dist/lib/ | tail -20

# Copy entrypoint script
COPY entrypoint.sh /opt/jposee/entrypoint.sh
RUN chmod +x /opt/jposee/entrypoint.sh

EXPOSE 5000 5001

WORKDIR /opt/jposee/dist

# Use entrypoint script to properly set classpath
ENTRYPOINT ["/opt/jposee/entrypoint.sh"]
