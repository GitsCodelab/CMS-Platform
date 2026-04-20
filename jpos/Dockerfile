FROM eclipse-temurin:17-jdk-jammy AS builder

# Download and extract the official jPOS distribution
RUN apt-get update && apt-get install -y --no-install-recommends curl tar && \
    cd /tmp && \
    curl -s -L -o jpos-dist.tar.gz https://sourceforge.net/projects/jpos/files/jPOS/2.1.8/jPOS-2.1.8.tar.gz/download 2>/dev/null || \
    curl -s -L -o jpos-dist.tar.gz https://repo1.maven.org/maven2/org/jpos/jpos-binary/2.1.8/jpos-binary-2.1.8.tar.gz 2>/dev/null || \
    echo "Distribution download failed" && \
    if [ -f jpos-dist.tar.gz ] && tar -tzf jpos-dist.tar.gz >/dev/null 2>&1; then \
      tar -xzf jpos-dist.tar.gz && \
      ls -la /tmp/ | head -20; \
    else \
      echo "jPOS distribution not available"; \
      mkdir -p /tmp/jpos-dist; \
    fi

FROM eclipse-temurin:17-jdk-jammy

WORKDIR /opt/jpos

# Copy jPOS distribution from builder
COPY --from=builder /tmp/jPOS-* /opt/jpos/dist/

# Copy any local files
COPY . /opt/jpos/

# Ensure core directories exist and populate from any local overrides
RUN mkdir -p /opt/jpos/dist/lib && \
    mkdir -p /opt/jpos/dist/deploy && \
    mkdir -p /opt/jpos/dist/config && \
    mkdir -p /opt/jpos/dist/log && \
    if [ -d /opt/jpos/deploy ]; then cp -r /opt/jpos/deploy/* /opt/jpos/dist/deploy/ 2>/dev/null || true; fi && \
    if [ -d /opt/jpos/config ]; then cp -r /opt/jpos/config/* /opt/jpos/dist/config/ 2>/dev/null || true; fi && \
    if [ -d /opt/jpos/lib ]; then cp -r /opt/jpos/lib/* /opt/jpos/dist/lib/ 2>/dev/null || true; fi && \
    chmod -R 755 /opt/jpos/dist && \
    chmod -R 777 /opt/jpos/dist/log && \
    ls -la /opt/jpos/dist/lib/ 2>/dev/null | head -10 || echo "Checking lib directory..."

# Download core jPOS runtime dependencies
RUN if [ ! -f /opt/jpos/dist/lib/jpos-2.1.8.jar ]; then \
      cd /opt/jpos/dist/lib && \
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
      curl -s -L -o commons-codec-1.15.jar https://repo1.maven.org/maven2/commons-codec/commons-codec/1.15/commons-codec-1.15.jar; \
    fi && \
    echo "jPOS dependencies downloaded" && \
    ls -lah /opt/jpos/dist/lib/ | tail -20

# Copy entrypoint script
COPY entrypoint.sh /opt/jpos/entrypoint.sh
RUN chmod +x /opt/jpos/entrypoint.sh

EXPOSE 5000

WORKDIR /opt/jpos/dist

# Use entrypoint script to properly set classpath
ENTRYPOINT ["/opt/jpos/entrypoint.sh"]