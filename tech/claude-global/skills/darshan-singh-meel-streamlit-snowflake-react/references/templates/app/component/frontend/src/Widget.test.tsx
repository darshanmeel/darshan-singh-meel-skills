import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { Widget } from "./Widget";

afterEach(cleanup);

describe("Widget", () => {
  it("marks the value from Python as pressed", () => {
    render(<Widget label="Grain" options={["Daily", "Weekly"]} value="Weekly" onPick={() => {}} />);
    expect(screen.getByRole("button", { name: "Weekly" }).getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByRole("button", { name: "Daily" }).getAttribute("aria-pressed")).toBe("false");
  });

  it("sends the clicked option once", () => {
    const onPick = vi.fn();
    render(<Widget label="Grain" options={["Daily", "Weekly"]} value={null} onPick={onPick} />);
    fireEvent.click(screen.getByRole("button", { name: "Daily" }));
    expect(onPick).toHaveBeenCalledTimes(1);
    expect(onPick).toHaveBeenCalledWith("Daily");
  });

  it("is read-only without a way back to Python", () => {
    render(<Widget label="Grain" options={["Daily"]} value={null} />);
    expect(screen.getByRole("button", { name: "Daily" }).closest("fieldset")?.disabled).toBe(true);
  });

  it("says so when there is nothing to show", () => {
    render(<Widget label="Grain" options={[]} value={null} onPick={() => {}} />);
    expect(screen.getByText("No options to show.")).toBeTruthy();
  });
});
