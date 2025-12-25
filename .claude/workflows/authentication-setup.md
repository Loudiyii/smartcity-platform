# Workflow: Authentication Setup

## Objectif
Implémenter l'authentification JWT avec Supabase Auth pour protéger les routes admin.

## Référence
- **User Story:** US-008
- **Skills:** `backend-api`, `frontend-dashboard`

## Étapes

### 1. Backend - Routes Auth
```python
# backend/app/api/v1/auth.py
@router.post("/login")
async def login(email: str, password: str):
    supabase = get_supabase_client()
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return {"access_token": response.session.access_token}
```

### 2. Frontend - Auth Store
```typescript
// frontend/src/stores/authStore.ts
export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  login: async (email, password) => {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({email, password})
    });
    const data = await res.json();
    set({ user: data.user, accessToken: data.access_token });
  }
}));
```

### 3. Protected Routes
```typescript
export const ProtectedRoute = ({ children }) => {
  const isAuth = useAuthStore(s => s.isAuthenticated);
  return isAuth ? children : <Navigate to="/login" />;
};
```

## Critères d'Acceptation
- [ ] Login functional
- [ ] Token stored
- [ ] Protected routes work
