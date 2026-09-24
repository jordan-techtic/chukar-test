import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { AppProvider } from "@/stores/AppContext";

describe("protected route", () => {
  it("redirects to login when no session exists", async () => {
    localStorage.clear();
    sessionStorage.clear();
    render(
      <AppProvider>
        <MemoryRouter initialEntries={["/calendar"]}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/calendar" element={<h1>Calendar</h1>} />
            </Route>
            <Route path="/login" element={<h1>Login</h1>} />
          </Routes>
        </MemoryRouter>
      </AppProvider>,
    );
    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Calendar" })).not.toBeInTheDocument();
  });
});
