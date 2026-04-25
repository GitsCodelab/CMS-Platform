FROM maven:3.8.1-openjdk-11 as builder

WORKDIR /app

# Copy pom.xml
COPY pom.xml .

# Download dependencies
RUN mvn dependency:resolve

# Copy source code
COPY src ./src

# Build the project without compiling stale test sources
RUN mvn clean package -Dmaven.test.skip=true

# Runtime image - use maven base since openjdk images unavailable
FROM maven:3.8.1-openjdk-11

WORKDIR /app

# Copy the shaded application jar
COPY --from=builder /app/target/jpos-ee-1.0.0.jar /app/app.jar

# Copy config
COPY config ./config

# Expose port
EXPOSE 8583

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD bash -lc "echo > /dev/tcp/127.0.0.1/8583"

# Run application
CMD ["java", "-jar", "app.jar"]
