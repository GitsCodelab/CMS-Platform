FROM maven:3.8.1-openjdk-11 as builder

WORKDIR /app

# Copy pom.xml
COPY pom.xml .

# Download dependencies
RUN mvn dependency:resolve

# Copy source code
COPY src ./src

# Build the project
RUN mvn clean package -DskipTests

# Runtime image - use maven base since openjdk images unavailable
FROM maven:3.8.1-openjdk-11

WORKDIR /app

# Copy built jar
COPY --from=builder /app/target/*.jar app.jar

# Copy config
COPY config ./config

# Expose port
EXPOSE 8583

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD nc -z localhost 8583 || exit 1

# Run application
CMD ["java", "-jar", "app.jar"]
