import time
from collections import defaultdict
from fastapi import HTTPException, status

GLOBAL_RATE_LIMIT = 3  # Maximum requests per minute
GLOBAL_TIME_WINDOW_SECONDS = 60  # 1 minute window

# Store request timestamps for each user
user_requests = defaultdict(list)

def apply_rate_limit(user_id: str):
    """
    Apply rate limiting for the specified user.
    Allows 3 requests per minute per user.
    """
    current_time = time.time()
    time_window = GLOBAL_TIME_WINDOW_SECONDS

    # Clean up old requests
    user_requests[user_id] = [
        t for t in user_requests[user_id] 
        if t > current_time - time_window
    ]

    # Check if user has exceeded rate limit
    if len(user_requests[user_id]) >= GLOBAL_RATE_LIMIT:
        remaining_time = int(time_window - (current_time - user_requests[user_id][0]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please try again in {remaining_time} seconds. Limit is {GLOBAL_RATE_LIMIT} requests per {time_window} seconds."
        )

    # Add current request timestamp
    user_requests[user_id].append(current_time)
    return True