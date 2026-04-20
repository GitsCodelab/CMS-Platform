#!/bin/bash
set -e

# Build classpath from all JARs in lib directory
CLASSPATH="/opt/jpos/dist/lib/*:/opt/jpos/dist"

# Debug output
echo "Starting jPOS..."
echo "Working directory: $(pwd)"
echo "CLASSPATH=$CLASSPATH"
echo "Java version:"
java -version

# List JARs present
echo "JARs in lib:"
ls -lah /opt/jpos/dist/lib/ 2>&1 | tail -10

# Run jPOS Q2
echo "Starting Q2..."
exec java -cp "$CLASSPATH" org.jpos.q2.Q2
