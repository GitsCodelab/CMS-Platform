👉 "add MAC validation end-to-end"


cd /home/samehabib/CMS-Platform/jpos-ee && pkill -f jpos-ee; sleep 2; java -jar target/jpos-ee-1.0.0.jar > /tmp/gateway.log 2>&1 &
sleep 4
python3 test-script/Production-raw-ISO.py 2>&1 | tail -40


ISO message (bytes)
        ↓
jPOS XML → parses structure
        ↓
ISOMsg object
        ↓
Java → processes logic
        ↓
ISOMsg response
        ↓
jPOS XML → packs back to bytes