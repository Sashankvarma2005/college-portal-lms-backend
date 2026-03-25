import React, { useMemo, useState } from "react";
import { apiPost, apiGet } from "./api.js";

const roleEndpoints = {
  student: "/api/auth/student/login",
  faculty: "/api/auth/faculty/login",
  admin: "/api/auth/admin/login",
};

export default function App() {
  const [role, setRole] = useState("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [token, setToken] = useState("");
  const [profile, setProfile] = useState(null);
  const [msg, setMsg] = useState("");

  const authHeader = useMemo(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  async function handleLogin(e) {
    e.preventDefault();
    setMsg("");
    setProfile(null);

    const endpoint = roleEndpoints[role];
    const resp = await apiPost(endpoint, { email, password });
    if (!resp.ok) {
      setMsg(resp.error || "Login failed.");
      return;
    }

    const data = await resp.json();
    setToken(data.token || "");
    setMsg(`Logged in as ${data.role}.`);
  }

  async function fetchStudentProfile() {
    setMsg("");
    setProfile(null);

    const resp = await apiGet("/api/student/profile", authHeader);
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      setMsg(data.message || "Profile fetch failed (RBAC may block).");
      return;
    }
    setProfile(data);
    setMsg("Profile fetched.");
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 24, maxWidth: 760 }}>
      <h1>Landmine Soft LMS Demo</h1>

      <div style={{ marginTop: 12 }}>
        <form onSubmit={handleLogin}>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <label>
              Role{" "}
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
                <option value="admin">Admin</option>
              </select>
            </label>

            <label>
              Email <input value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>

            <label>
              Password{" "}
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </label>
          </div>

          <div style={{ marginTop: 12 }}>
            <button type="submit">Login</button>
          </div>
        </form>
      </div>

      {token ? (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 13, opacity: 0.8 }}>JWT token (truncated):</div>
          <pre style={{ background: "#f5f5f5", padding: 12, borderRadius: 8, overflow: "auto" }}>
            {token.slice(0, 60)}...
          </pre>
        </div>
      ) : null}

      <div style={{ marginTop: 18 }}>
        <button onClick={fetchStudentProfile} disabled={!token}>
          Get /api/student/profile (RBAC)
        </button>
      </div>

      {msg ? <div style={{ marginTop: 10 }}>{msg}</div> : null}

      {profile ? (
        <div style={{ marginTop: 16 }}>
          <h2>Student Profile</h2>
          <pre style={{ background: "#f5f5f5", padding: 12, borderRadius: 8 }}>
            {JSON.stringify(profile, null, 2)}
          </pre>
        </div>
      ) : null}
    </div>
  );
}

