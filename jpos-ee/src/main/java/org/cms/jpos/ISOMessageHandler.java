package org.cms.jpos;

import java.util.*;
import java.util.logging.Logger;
import java.util.logging.Level;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.IvParameterSpec;
import java.io.ByteArrayOutputStream;
import java.util.Arrays;

public class ISOMessageHandler {

    private static final Logger logger = Logger.getLogger(ISOMessageHandler.class.getName());

    // 🔐 Shared MAC key (must match client)
    private static final byte[] MAC_KEY =
        hexToBytes("0123456789ABCDEFFEDCBA9876543210");

    public static class SimpleISOMessage {
        private String mti;
        private Map<Integer,String> fields = new HashMap<>();

        public void setMTI(String m){mti=m;}
        public String getMTI(){return mti;}
        public void set(int f,String v){fields.put(f,v);}
        public boolean hasField(int f){return fields.containsKey(f);}
        public String getString(int f){return fields.getOrDefault(f,"");}
        public String get(int f){return fields.getOrDefault(f,"");}
        public Map<Integer,String> getFields(){return fields;}
    }

    // ================= MAIN =================
    public static byte[] processRawMessage(byte[] message, int length) {
        try {

            int pos = 5;

            String mti = new String(message,pos,4);
            pos+=4;

            long bitmap=0;
            for(int i=0;i<8;i++){
                bitmap=(bitmap<<8)|(message[pos+i]&0xFF);
            }
            pos+=8;

            SimpleISOMessage req=new SimpleISOMessage();
            req.setMTI(mti);

            for(int f=2;f<=64;f++){
                if((bitmap&(1L<<(64-f)))!=0){
                    int start=pos;
                    String val=parseField(message,pos,f);
                    if(val!=null){
                        req.set(f,val);
                        pos=updatePos(message,start,f);
                    }else{
                        pos=updatePos(message,start,f);
                    }
                }
            }

            // 🔐 MAC VALIDATION
            if(req.hasField(64)){
                String recMac = req.getString(64);
                String calcMac = calculateMACForMessage(req);

                if(!recMac.equals(calcMac)){
                    return error("0210","96");
                }
            }

            // 🔐 PIN (DUKPT hook)
            if(req.hasField(52)){
                if(!validateDUKPT(req)){
                    return error("0210","55");
                }
            }

            // 🔐 EMV (ARQC hook)
            if(req.hasField(55)){
                Map<String,String> tlv=parseTLV(req.getString(55));
                if(tlv.containsKey("9F26")){
                    if(!validateARQC(tlv)){
                        return error("0210","05");
                    }
                }
            }

            SimpleISOMessage resp = process(req);

            // 🔐 Add response MAC if request had MAC
            if(req.hasField(64)){
                resp.set(64, calculateMACForMessage(resp));
            }

            return serialize(resp);

        } catch(Exception e){
            logger.log(Level.SEVERE,"Error",e);
            return null;
        }
    }

    // ================= BUSINESS =================
    private static SimpleISOMessage process(SimpleISOMessage req){
        SimpleISOMessage resp=new SimpleISOMessage();

        switch(req.getMTI()){
            case "0100":  // Authorization Request → Authorization Response
                resp.setMTI("0110");
                resp.set(39,"00");
                resp.set(38,"123456");  // Auth Code
                break;

            case "0200":  // Balance Inquiry Request → Balance Inquiry Response
                resp.setMTI("0210");
                resp.set(39,"00");
                resp.set(54,"840000000000001000");  // Balance
                break;

            case "0220":  // Financial Transaction Request → Financial Transaction Response
                resp.setMTI("0230");
                resp.set(39,"00");
                resp.set(38,"123456");  // Auth Code
                break;

            case "0400":  // Reversal Request → Reversal Response
                resp.setMTI("0410");
                resp.set(39,"00");
                resp.set(38,"654321");  // Reversal Auth Code
                break;

            case "0500":  // Logoff Request → Logoff Response
                resp.setMTI("0510");
                resp.set(39,"00");
                break;

            case "0600":  // PIN Change Request → PIN Change Response
                resp.setMTI("0610");
                resp.set(39,"00");
                break;

            case "0800":  // Echo Test Request → Echo Test Response
                resp.setMTI("0810");
                resp.set(39,"00");
                break;

            default:  // Unknown message type
                resp.setMTI("9999");
                resp.set(39,"30");  // Unknown message type error
        }

        // Copy relevant fields from request to response
        if(req.hasField(2)) resp.set(2, req.getString(2));   // PAN
        if(req.hasField(4)) resp.set(4, req.getString(4));   // Amount
        if(req.hasField(11)) resp.set(11,req.getString(11)); // STAN
        if(req.hasField(12)) resp.set(12,req.getString(12)); // Time
        if(req.hasField(13)) resp.set(13,req.getString(13)); // Date
        
        return resp;
    }

    // ================= ERROR =================
    private static byte[] error(String mti,String code)throws Exception{
        SimpleISOMessage e=new SimpleISOMessage();
        e.setMTI(mti);
        e.set(39,code);
        return serialize(e);
    }

    // ================= SERIALIZE =================
    private static byte[] serialize(SimpleISOMessage msg)throws Exception{

        long bitmap=0;
        for(int f:msg.getFields().keySet()){
            bitmap|=(1L<<(64-f));
        }

        ByteArrayOutputStream baos=new ByteArrayOutputStream();
        baos.write(new byte[]{0x60,0,0,0,0});
        baos.write(msg.getMTI().getBytes());

        for(int i=7;i>=0;i--){
            baos.write((byte)(bitmap>>(i*8)));
        }

        for(int f=2;f<=64;f++){
            if(msg.hasField(f)){
                writeField(baos,f,msg.getString(f));
            }
        }

        return baos.toByteArray();
    }

    // ================= MAC =================
    private static String calculateMACForMessage(SimpleISOMessage msg)throws Exception{

        SimpleISOMessage tmp=new SimpleISOMessage();
        tmp.setMTI(msg.getMTI());

        for(int f:msg.getFields().keySet()){
            if(f!=64) tmp.set(f,msg.getString(f));
        }

        byte[] body=serialize(tmp);
        byte[] mac=calculateMAC(body);

        return toHex(mac,0,mac.length);
    }

    private static byte[] calculateMAC(byte[] data)throws Exception{
        Cipher c=Cipher.getInstance("DESede/CBC/NoPadding");
        SecretKeySpec key=new SecretKeySpec(MAC_KEY,"DESede");

        int len=((data.length+7)/8)*8;
        byte[] padded=Arrays.copyOf(data,len);

        c.init(Cipher.ENCRYPT_MODE,key,new IvParameterSpec(new byte[8]));
        byte[] out=c.doFinal(padded);

        return Arrays.copyOfRange(out,out.length-8,out.length);
    }

    // ================= DUKPT (HOOK) =================
    private static boolean validateDUKPT(SimpleISOMessage req){
        String pin=req.getString(52);
        return pin.length()==16;
    }

    // ================= EMV =================
    private static Map<String,String> parseTLV(String hex){
        Map<String,String> map=new HashMap<>();
        int i=0;
        while(i<hex.length()){
            String tag=hex.substring(i,i+2);i+=2;
            int len=Integer.parseInt(hex.substring(i,i+2),16)*2;i+=2;
            String val=hex.substring(i,i+len);i+=len;
            map.put(tag,val);
        }
        return map;
    }

    private static boolean validateARQC(Map<String,String> tlv){
        return true; // placeholder
    }

    // ================= FIELD =================
    private static String parseField(byte[] m,int pos,int f){
        try{
            switch(f){
                case 2:return new String(m,pos+2,Integer.parseInt(new String(m,pos,2)));
                case 3:return new String(m,pos,6);
                case 11:return new String(m,pos,6);
                case 52:return toHex(m,pos,8);
                case 55:
                    int l=Integer.parseInt(new String(m,pos,3));
                    return toHex(m,pos+3,l);
                case 64:
                    return toHex(m,pos,8);
            }
        }catch(Exception e){}
        return null;
    }

    private static int updatePos(byte[] m,int pos,int f){
        switch(f){
            case 2:return pos+2+Integer.parseInt(new String(m,pos,2));
            case 55:return pos+3+Integer.parseInt(new String(m,pos,3));
            case 52:return pos+8;
            case 64:return pos+8;
            case 3:return pos+6;
            case 11:return pos+6;
        }
        return pos;
    }

    private static void writeField(ByteArrayOutputStream b,int f,String v)throws Exception{
        switch(f){
            case 2:  // PAN - LLVAR
                b.write(String.format("%02d",v.length()).getBytes());
                b.write(v.getBytes());
                break;
            case 4:  // Amount - FIXED 12
                b.write(String.format("%012d", Long.parseLong(v.replaceAll("[^0-9]",""))).getBytes());
                break;
            case 11: // STAN - FIXED 6
            case 12: // Time - FIXED 6
            case 13: // Date - FIXED 4
            case 38: // Auth Code - FIXED 6
            case 39: // Response Code - FIXED 2
                b.write(v.getBytes());
                break;
            case 54: // Balance - LLVAR
                b.write(String.format("%02d",v.length()).getBytes());
                b.write(v.getBytes());
                break;
            case 55: // EMV TLV - LLLVAR
                b.write(String.format("%03d",v.length()).getBytes());
                b.write(v.getBytes());
                break;
            case 64: // MAC - BINARY
                b.write(hexToBytes(v));
                break;
        }
    }

    private static String toHex(byte[] d,int o,int l){
        StringBuilder sb=new StringBuilder();
        for(int i=0;i<l;i++) sb.append(String.format("%02X",d[o+i]));
        return sb.toString();
    }

    private static byte[] hexToBytes(String hex){
        byte[] out=new byte[hex.length()/2];
        for(int i=0;i<out.length;i++){
            out[i]=(byte)Integer.parseInt(hex.substring(i*2,i*2+2),16);
        }
        return out;
    }

    public static SimpleISOMessage processMessage(SimpleISOMessage req) {
        return process(req);
    }

    public static void clearTransactionLog() {
        // Transaction log clearing (stub for compatibility)
    }

}