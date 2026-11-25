import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChangePasswordPanel } from "@/components/ChangePasswordPanel";

describe("ChangePasswordPanel", () => {
  beforeEach(() => {
    global.fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ status: "ok" }),
    })) as unknown as typeof fetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("rejects mismatched confirmation without calling the API", async () => {
    render(<ChangePasswordPanel token="test-token" onClose={vi.fn()} />);

    await userEvent.type(screen.getByLabelText("Contraseña actual"), "actual123");
    await userEvent.type(screen.getByLabelText("Nueva contraseña"), "nueva123");
    await userEvent.type(screen.getByLabelText("Confirmar nueva contraseña"), "otra456");
    await userEvent.click(screen.getByRole("button", { name: /guardar nueva contraseña/i }));

    expect(await screen.findByText(/no coinciden/i)).toBeInTheDocument();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it("submits the password change and shows a success message", async () => {
    render(<ChangePasswordPanel token="test-token" onClose={vi.fn()} />);

    await userEvent.type(screen.getByLabelText("Contraseña actual"), "actual123");
    await userEvent.type(screen.getByLabelText("Nueva contraseña"), "nueva123");
    await userEvent.type(screen.getByLabelText("Confirmar nueva contraseña"), "nueva123");
    await userEvent.click(screen.getByRole("button", { name: /guardar nueva contraseña/i }));

    await waitFor(() =>
      expect(global.fetch).toHaveBeenCalledWith("/api/users/me/password", expect.any(Object))
    );
    expect(await screen.findByText(/actualizada correctamente/i)).toBeInTheDocument();
  });
});
