import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "@/components/LoginForm";

describe("LoginForm", () => {
  it("does not reveal seeded credentials", () => {
    render(<LoginForm onLogin={vi.fn()} onRegister={vi.fn()} />);
    expect(screen.queryByText(/usuario \/ contraseña/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/prueba con/i)).not.toBeInTheDocument();
  });

  it("submits login credentials in login mode", async () => {
    const onLogin = vi.fn();
    render(<LoginForm onLogin={onLogin} onRegister={vi.fn()} />);

    await userEvent.type(screen.getByLabelText("Usuario"), "alguien");
    await userEvent.type(screen.getByLabelText("Contraseña"), "clave123");
    await userEvent.click(screen.getByRole("button", { name: /iniciar sesión/i }));

    expect(onLogin).toHaveBeenCalledWith("alguien", "clave123");
  });

  it("switches to register mode and submits registration data", async () => {
    const onRegister = vi.fn();
    render(<LoginForm onLogin={vi.fn()} onRegister={onRegister} />);

    await userEvent.click(screen.getByRole("button", { name: /regístrate/i }));
    expect(screen.getByLabelText("Nombre visible")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText("Usuario"), "nuevo");
    await userEvent.type(screen.getByLabelText("Nombre visible"), "Nueva Persona");
    await userEvent.type(screen.getByLabelText("Contraseña"), "clave123");
    await userEvent.click(screen.getByRole("button", { name: /crear cuenta/i }));

    expect(onRegister).toHaveBeenCalledWith("nuevo", "clave123", "Nueva Persona");
  });
});
