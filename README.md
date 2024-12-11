# API Endpoints



<details>
 <summary><code>GET</code> <code><b>/</b></code> <code>(main endpoint)</code></summary>

##### Parameters
> None

##### Request Body
> None


##### Response Body

```json
{
"status": "success", 
"message": "WijiWaste API is running..."
}
```
</details>


#### Predictions

<details>
 <summary><code>POST</code> <code><b>/predict</b></code> <code>(make prediction)</code></summary>


##### Request Body
```json
{
   "file": "image"
}
```

##### Response Body
```json
{
    "prediction_id": int,
    "prediction": int,
    "confidence": float,
    "message": string,
    "timestamp": string,
    "image_url": string,
}
```
</details>

<details>
 <summary><code>GET</code> <code><b>/predictions</b></code> <code>(get all predictions)</code></summary>


##### Request Body
> None

##### Response Body
```json
{
    "predictions": [
        {
            
            "prediction_id": int,
            "prediction": int,
            "confidence": float,
            "message": string,
            "timestamp": string,
            "image_url": string,
        },
        
        {
            "prediction_id": int,
            "prediction": int,
            "confidence": float,
            "message": string,
            "timestamp": string,
            "image_url": string,
        }
    ]
}
```
</details>

<details>
 <summary><code>GET</code> <code><b>/predictions/{doc_id}</b></code> <code>(get prediction by id)</code></summary>

##### Path Parameter
> | name | type | data type |
> |-----------|-----------|-------------------------|
> | doc_id | required | string|


##### Response Body
```json
{
    "prediction_id": int,
    "prediction": int,
    "confidence": float,
    "message": string,
    "timestamp": string,
    "image_url": string,
}
```
</details>

<details>
 <summary><code>GET</code> <code><b>/predictions/{doc_id}/{field}</b></code> <code>(get spesific field from id)</code></summary>

##### Path Parameter
> | name | type | data type |
> |-----------|-----------|-------------------------|
> | doc_id | required | string|
> | field | required | string|

##### Request Body
> None

##### Response Body
```json
{
    "field_content": "string"
}
```
</details>








