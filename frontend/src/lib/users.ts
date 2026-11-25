import { apiError, authedFetch } from "@/lib/api";

export type Role = "admin" | "member";

export type UserSummary = {
  id: string;
  username: string;
  display_name: string | null;
  role: Role;
  created_at: string;
};

export const listUsers = async (token: string): Promise<UserSummary[]> => {
  const response = await authedFetch(token, "/api/users");
  if (!response.ok) {
    return apiError(response, "No se pudieron cargar los usuarios");
  }
  return response.json();
};

export const createUser = async (
  token: string,
  username: string,
  password: string,
  displayName: string,
  role: Role
): Promise<UserSummary> => {
  const response = await authedFetch(token, "/api/users", {
    method: "POST",
    body: JSON.stringify({ username, password, display_name: displayName, role }),
  });
  if (!response.ok) {
    return apiError(response, "No se pudo crear el usuario");
  }
  return response.json();
};

export const updateUserRole = async (
  token: string,
  userId: string,
  role: Role
): Promise<UserSummary> => {
  const response = await authedFetch(token, `/api/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify({ role }),
  });
  if (!response.ok) {
    return apiError(response, "No se pudo actualizar el usuario");
  }
  return response.json();
};

export const deleteUser = async (token: string, userId: string): Promise<void> => {
  const response = await authedFetch(token, `/api/users/${userId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    await apiError(response, "No se pudo eliminar el usuario");
  }
};

export const changePassword = async (
  token: string,
  currentPassword: string,
  newPassword: string
): Promise<void> => {
  const response = await authedFetch(token, "/api/users/me/password", {
    method: "POST",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
  if (!response.ok) {
    await apiError(response, "No se pudo cambiar la contraseña");
  }
};
