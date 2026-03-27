#!/usr/bin/env python3
"""
MidiMotion - macOS Host Application
Receives MIDI hit signals from the MidiMotion device and provides
controls for hit sensitivity.

Dependencies: pip install mido python-rtmidi
"""

import tkinter as tk
from tkinter import ttk
import mido


class MidiMotionApp:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MidiMotion")
        self.root.geometry("440x500")
        self.root.resizable(False, False)

        self._sensitivity_int = 10        # read by callback thread — plain int
        self._port            = None      # open mido port
        self._port_name       = ""        # currently open port name

        self._build_ui()
        self._refresh_ports()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 6}

        # ---- Port selection ----
        port_frame = ttk.LabelFrame(self.root, text="MIDI-sisääntulo")
        port_frame.pack(fill="x", **pad)

        self._port_var = tk.StringVar(value="— ei porttia —")
        self._port_var.trace_add("write", self._on_port_changed)

        self._port_menu = tk.OptionMenu(port_frame, self._port_var, "— ei porttia —")
        self._port_menu.config(width=30, anchor="w")
        self._port_menu.pack(side="left", padx=6, pady=6)

        ttk.Button(port_frame, text="Päivitä", command=self._refresh_ports).pack(
            side="left", padx=4
        )

        # Status dot
        self._status_dot = tk.Label(port_frame, text="●", fg="#555", font=("Helvetica", 16))
        self._status_dot.pack(side="right", padx=8)

        # ---- Sensitivity ----
        sens_frame = ttk.LabelFrame(self.root, text="Iskuherkkyys  (min. velocity 1–127)")
        sens_frame.pack(fill="x", **pad)

        self._sens_var = tk.IntVar(value=10)
        ttk.Scale(
            sens_frame, from_=1, to=127,
            orient="horizontal", variable=self._sens_var,
            command=self._on_sens_change,
        ).pack(fill="x", padx=10, pady=(6, 0))

        self._sens_lbl = ttk.Label(sens_frame, text="10")
        self._sens_lbl.pack(pady=(0, 6))

        # ---- Hit indicator ----
        hit_frame = ttk.LabelFrame(self.root, text="Iskuindikaattori")
        hit_frame.pack(fill="both", expand=True, **pad)

        self._canvas = tk.Canvas(hit_frame, height=140, bg="#111", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True, padx=8, pady=6)
        self._circle = self._canvas.create_oval(
            110, 10, 290, 130, fill="#222", outline="#333", width=2
        )

        self._vel_lbl = ttk.Label(hit_frame, text="Velocity: —", font=("Helvetica", 13))
        self._vel_lbl.pack(pady=(0, 8))

        # ---- Log ----
        log_frame = ttk.LabelFrame(self.root, text="Tapahtumaloki")
        log_frame.pack(fill="x", **pad)

        self._log_text = tk.Text(
            log_frame, height=5, state="disabled",
            bg="#0a0a0a", fg="#88ff88", font=("Menlo", 11), relief="flat",
        )
        self._log_text.pack(fill="x", padx=6, pady=6)

    # ------------------------------------------------------------------
    # Port management
    # ------------------------------------------------------------------

    def _refresh_ports(self) -> None:
        ports = mido.get_input_names()

        menu = self._port_menu["menu"]
        menu.delete(0, "end")
        for p in ports:
            menu.add_command(label=p, command=lambda name=p: self._port_var.set(name))

        if not ports:
            self._port_var.set("— ei porttia —")
            return

        # Keep current selection if still valid
        if self._port_var.get() in ports:
            return

        # Auto-prefer MidiMotion, fall back to first port
        preferred = next(
            (p for p in ports if any(kw in p.lower() for kw in ("midimotion", "esp32"))),
            ports[0],
        )
        self._port_var.set(preferred)

    def _on_port_changed(self, *_) -> None:
        name = self._port_var.get()
        if name == "— ei porttia —" or name == self._port_name:
            return
        self._open_port(name)

    def _open_port(self, name: str) -> None:
        self._close_port()
        try:
            self._port = mido.open_input(name, callback=self._midi_callback)
            self._port_name = name
            self._set_status(True)
            self._log(f"Avattu: {name}")
        except Exception as exc:
            self._port_name = ""
            self._set_status(False)
            self._log(f"Virhe: {exc}")

    def _close_port(self) -> None:
        if self._port is not None:
            try:
                self._port.close()
            except Exception:
                pass
            self._port = None
        self._port_name = ""
        self._set_status(False)

    # ------------------------------------------------------------------
    # MIDI callback  (rtmidi background thread — no tkinter calls here)
    # ------------------------------------------------------------------

    def _midi_callback(self, msg: mido.Message) -> None:
        print(f"MIDI in: {msg}")          # visible in terminal for debugging
        if msg.type == "note_on" and msg.velocity > 0:
            vel = msg.velocity
            if vel >= self._sensitivity_int:
                self.root.after(0, self._on_hit, msg.channel, msg.note, vel)

    # ------------------------------------------------------------------
    # UI updates  (main thread)
    # ------------------------------------------------------------------

    def _on_hit(self, channel: int, note: int, velocity: int) -> None:
        color = self._vel_color(velocity)
        self._canvas.itemconfig(self._circle, fill=color, outline=color)
        self._vel_lbl.config(text=f"Velocity: {velocity}")
        self._log(f"Isku  ch={channel + 1}  note={note}  vel={velocity}")
        self.root.after(180, lambda: self._canvas.itemconfig(
            self._circle, fill="#222", outline="#333"
        ))

    def _on_sens_change(self, _=None) -> None:
        v = int(self._sens_var.get())
        self._sensitivity_int = v
        self._sens_lbl.config(text=str(v))

    def _set_status(self, connected: bool) -> None:
        self._status_dot.config(fg="#22cc44" if connected else "#555")

    def _log(self, text: str) -> None:
        self._log_text.config(state="normal")
        self._log_text.insert("end", text + "\n")
        self._log_text.see("end")
        self._log_text.config(state="disabled")

    @staticmethod
    def _vel_color(v: int) -> str:
        t = v / 127.0
        return f"#{int(t*255):02x}{int((1-t)*200):02x}00"


# ----------------------------------------------------------------------

def main() -> None:
    root = tk.Tk()
    app = MidiMotionApp(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
