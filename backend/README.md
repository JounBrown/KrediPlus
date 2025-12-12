# KrediPlus RAG Backend

## Supabase Auth Integration

1. Create the following environment variables in `.env` (or your hosting secrets):
	- `SUPABASE_URL`: Project URL (e.g. `https://xyzcompany.supabase.co`).
	- `SUPABASE_KEY`: Public `anon` key (used only for client SDK calls).
	- `SUPABASE_SERVICE_KEY`: Service role key (used by background jobs and admin calls).
	- `SUPABASE_JWT_SECRET`: Value shown in the Supabase dashboard under **Project Settings → API → JWT Secret**. The backend uses this secret to validate the access tokens issued by Supabase Auth. If you rotate the JWT secret, redeploy the backend with the new value.

2. The frontend must send the Supabase access token on every request after login:

	```http
	Authorization: Bearer <supabase-access-token>
	```

	The FastAPI dependency `get_current_user` (declared in `src/api/middleware/auth_middleware.py`) reads the token from the `Authorization` header, verifies it against Supabase, and injects the authenticated `User` into every protected route.

3. Routers `clients`, `credits`, `documents` and `simulator` require a valid session for all operations. `loan_applications` keeps `POST /loan_applications` public for intake forms, while the rest of the actions (list, update, delete) are protected. Configuration mutations inside the simulator additionally depend on `require_admin`, so only users with `role = "admin"` in their Supabase metadata can touch those endpoints.

4. On startup FastAPI will raise `401 Unauthorized` if the token is missing/invalid and `403 Forbidden` if the authenticated user lacks admin privileges for specific actions. This mirrors the Supabase Auth state from the frontend session, so the only requirement is to forward the access token that Supabase already returns after login.

Run the server with `uvicorn src.main:app --reload` (see `src/config.py` for host/port flags). Use the `/health` endpoint to verify connectivity before testing authenticated calls.
