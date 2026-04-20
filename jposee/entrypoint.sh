#!/bin/bash
set -e

# Build classpath from all JARs in lib directory
CLASSPATH="/opt/jposee/dist/lib/*:/opt/jposee/dist"

# Debug output
echo "Starting jPOS EE..."
echo "Working directory: $(pwd)"
echo "CLASSPATH=$CLASSPATH"
echo "Java version:"
java -version

# List JARs present
echo "JARs in lib:"
ls -lah /opt/jposee/dist/lib/ 2>&1 | tail -10

# Run jPOS Q2
echo "Starting Q2..."
exec java -cp "$CLASSPATH" org.jpos.q2.Q2
