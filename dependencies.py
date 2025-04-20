from fastapi import Header, Query, HTTPException

def get_query_token(token: str = Query(...)):
    if token != "expected_token":
        raise HTTPException(status_code=403, detail="Invalid token")
    return token

def get_token_header(x_token: str = Header(...)):
    if x_token != "expected_token":
        raise HTTPException(status_code=403, detail="Invalid token")
    return x_token