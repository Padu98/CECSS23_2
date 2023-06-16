package com;

public class DBObj {

    public DBObj(){

    }

    private String id;
    private String deviceId;
    private double voltage;
    private int humidity;

    public void setId(String newId){
        id = newId;
    }

    public String getId(){
        return id;
    }

    public void setDeviceId(String devId){
        deviceId = devId;
    }

    public String getDeviceId(){
        return deviceId;
    }

    public void setVoltage(double vol){
        voltage = vol;
    }

    public double getVoltage(){
        return voltage;
    }

    public void setHumidity(int hum){
        humidity = hum;
    }

    public int getHumidity(){
        return humidity;
    }
    
}
