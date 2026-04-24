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
                if(!validateMAC(message)){
                    logger.warning("MAC FAILED");

                    SimpleISOMessage err=new SimpleISOMessage();
                    err.setMTI("0210");
                    err.set(39,"96");
                    return serialize(err);
                }
            }

            // 🔐 PIN VALIDATION
            if(req.hasField(52)){
                String pin=req.getString(52);
                if(pin.length()!=16){
                    SimpleISOMessage err=new SimpleISOMessage();
                    err.setMTI("0210");
                    err.set(39,"55");
                    return serialize(err);
                }
            }

            // 🔐 EMV TLV + ARQC
            if(req.hasField(55)){
                Map<String,String> tlv=parseTLV(req.getString(55));

                if(tlv.containsKey("9F26")){
                    if(!validateARQC(tlv)){
                        SimpleISOMessage err=new SimpleISOMessage();
                        err.setMTI("0210");
                        err.set(39,"05");
                        return serialize(err);
                    }
                }
            }

            SimpleISOMessage resp = process(req);

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

        byte[] body=baos.toByteArray();

        // 🔐 ADD MAC
        byte[] mac=calculateMAC(body);
        baos.write(mac);

        byte[] finalMsg=baos.toByteArray();

        return finalMsg;
    }

    // ================= MAC =================
    private static boolean validateMAC(byte[] msg)throws Exception{
        if(msg.length<8) return false;

        byte[] body=Arrays.copyOf(msg,msg.length-8);
        byte[] rec=Arrays.copyOfRange(msg,msg.length-8,msg.length);

        byte[] calc=calculateMAC(body);

        return Arrays.equals(rec,calc);
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
        logger.info("ARQC check (stub)");
        return true;
    }

    // ================= FIELD =================
    private static String parseField(byte[] m,int pos,int f){
        try{
            switch(f){
                case 2:return new String(m,pos+2,Integer.parseInt(new String(m,pos,2)));
                case 3:return new String(m,pos,6);
                case 11:return new String(m,pos,6);
                case 41:return new String(m,pos,8);
                case 42:return new String(m,pos,15);
                case 49:return new String(m,pos,3);
                case 52:return toHex(m,pos,8);
                case 55:
                    int l=Integer.parseInt(new String(m,pos,3));
                    return toHex(m,pos+3,l);
            }
        }catch(Exception e){}
        return null;
    }

    private static int updatePos(byte[] m,int pos,int f){
        switch(f){
            case 2:return pos+2+Integer.parseInt(new String(m,pos,2));
            case 55:return pos+3+Integer.parseInt(new String(m,pos,3));
            case 52:return pos+8;
            case 3:return pos+6;
            case 11:return pos+6;
            case 41:return pos+8;
            case 42:return pos+15;
            case 49:return pos+3;
        }
        return pos;
    }

    private static void writeField(ByteArrayOutputStream b,int f,String v)throws Exception{
        if(f==11) b.write(v.getBytes());
        if(f==39) b.write(v.getBytes());
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