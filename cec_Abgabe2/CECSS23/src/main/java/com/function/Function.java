package com.function;

import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.annotation.FunctionName;

import netscape.javascript.JSException;
import com.DBObj;

import com.microsoft.azure.functions.annotation.EventHubTrigger;
import org.json.JSONObject;
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;
import java.util.UUID;
import org.json.JSONArray;
import com.azure.cosmos.CosmosClientBuilder;
import com.azure.cosmos.CosmosClient;
import com.azure.cosmos.CosmosDatabase;
import com.azure.cosmos.CosmosContainer;
import com.azure.cosmos.models.PartitionKey;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.DefaultAzureCredential;
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;
import com.azure.cosmos.models.CosmosItemRequestOptions;


public class Function {
    @FunctionName("humiditySensorFunction")
    public void eventHubProcessor(
    @EventHubTrigger(name = "myTrigger", eventHubName = "ampaduHub", connection = "functionConnection") String message, 
    
   // @CosmosDBOutput(name = "database", databaseName = "cecdb", containerName = "humidity", connection = "cec_cosmosdb") OutputBinding<String> outputItem,

    final ExecutionContext context ){
        try{
            JSONArray jsonArray = new JSONArray(message);
            JSONObject json = jsonArray.getJSONObject(0);
            if(json.has("humidity") && json.has("deviceId")){
                UUID uuid = UUID.randomUUID();
                DBObj reply = new DBObj();
                reply.setId(uuid.toString());
                reply.setDeviceId(json.getString("deviceId"));
                reply.setHumidity(json.getInt("humidity"));
                reply.setVoltage(json.getDouble("voltage"));

                this.createManagedIdentityCredentialAndInsertToDB(reply, context);
                //outputItem.setValue(answer.toString());
            }
        }catch(JSException ex){
            context.getLogger().info("converting to json failed");
        }
    }

    private void createManagedIdentityCredentialAndInsertToDB(DBObj answer, ExecutionContext context) {
        DefaultAzureCredential  defaultCredential = new DefaultAzureCredentialBuilder()
            .managedIdentityClientId("fe1d2312-f6b8-4cac-a56b-c4ff8825acad")
            .build();        
        SecretClient secretClient = new SecretClientBuilder()
            .vaultUrl("https://ampaduspace9755389494.vault.azure.net/") 
            .credential(defaultCredential)
            .buildClient();
        
        KeyVaultSecret secret = secretClient.getSecret("cosmosdbcec");
        CosmosClient cosmosClient = new CosmosClientBuilder()
            .endpoint("https://ampadb.documents.azure.com:443/")
            .key(secret.getValue())
            .buildClient();
        CosmosDatabase cosmosDatabase = cosmosClient.getDatabase("cecdb");
        CosmosContainer cosmosContainer = cosmosDatabase.getContainer("humidity");

        cosmosContainer.createItem(answer, new PartitionKey(answer.getDeviceId()), new CosmosItemRequestOptions());
        cosmosClient.close();
    }
}
