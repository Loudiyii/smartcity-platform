/**
 * Authentication hook for login, register, and password reset
 */

import { useMutation } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

// ===== Types =====

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
    full_name?: string
  }
}

export interface MessageResponse {
  message: string
}

// ===== Mutations =====

/**
 * Login user with email and password
 */
export function useLogin() {
  return useMutation<AuthResponse, Error, LoginCredentials>({
    mutationFn: async (credentials) => {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/auth/login`,
        credentials
      )
      // Store token in localStorage
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      return response.data
    }
  })
}

/**
 * Register new user account
 */
export function useRegister() {
  return useMutation<AuthResponse, Error, RegisterData>({
    mutationFn: async (userData) => {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/auth/register`,
        userData
      )
      // Store token in localStorage
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }
      return response.data
    }
  })
}

/**
 * Request password reset email
 */
export function useForgotPassword() {
  return useMutation<MessageResponse, Error, { email: string }>({
    mutationFn: async ({ email }) => {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/auth/forgot-password`,
        { email }
      )
      return response.data
    }
  })
}

/**
 * Reset password with token
 */
export function useResetPassword() {
  return useMutation<MessageResponse, Error, { token: string; new_password: string }>({
    mutationFn: async ({ token, new_password }) => {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/auth/reset-password`,
        { token, new_password }
      )
      return response.data
    }
  })
}

/**
 * Logout current user
 */
export function useLogout() {
  return useMutation<MessageResponse, Error>({
    mutationFn: async () => {
      const response = await axios.post(`${API_BASE_URL}/api/v1/auth/logout`)
      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      return response.data
    }
  })
}

// ===== Helper Functions =====

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token')
}

/**
 * Get current user from localStorage
 */
export function getCurrentUser() {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

/**
 * Get access token
 */
export function getAccessToken(): string | null {
  return localStorage.getItem('access_token')
}
