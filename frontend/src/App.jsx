import React, { useEffect, useMemo, useState } from "react";
import { apiPost, apiGet } from "./api.js";

const roleEndpoints = {
  student: "/api/auth/student/login",
  faculty: "/api/auth/faculty/login",
  admin: "/api/auth/admin/login",
};

export default function App() {
  const [role, setRole] = useState(localStorage.getItem("role") || "student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [profile, setProfile] = useState(null);
  const [announcements, setAnnouncements] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const authHeader = useMemo(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      localStorage.setItem("role", role);
    } else {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
    }
  }, [token, role]);

  async function handleLogin(e) {
    e.preventDefault();
    setMsg("");
    setProfile(null);
    setAnnouncements([]);
    setEnrollments([]);
    setLoading(true);

    try {
      const endpoint = roleEndpoints[role];
      const resp = await apiPost(endpoint, { email, password });

      if (!resp.ok) {
        setMsg(resp.error || "Login failed.");
        setLoading(false);
        return;
      }

      const data = await resp.json();
      setToken(data.token || "");
      setMsg(`Logged in successfully as ${data.role}.`);
    } catch (error) {
      setMsg("Something went wrong during login.");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    setToken("");
    setProfile(null);
    setAnnouncements([]);
    setEnrollments([]);
    setMsg("Logged out.");
  }

  async function fetchStudentProfile() {
    setMsg("");
    setProfile(null);
    setLoading(true);

    try {
      const resp = await apiGet("/api/student/profile", authHeader);
      const data = await resp.json().catch(() => ({}));

      if (!resp.ok) {
        setMsg(data.message || "Profile fetch failed.");
        setLoading(false);
        return;
      }

      setProfile(data);
      setMsg("Profile fetched successfully.");
    } catch (error) {
      setMsg("Could not fetch profile.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchAnnouncements() {
    setMsg("");
    setLoading(true);

    try {
      const resp = await apiGet("/api/announcements/", authHeader);
      const data = await resp.json().catch(() => []);

      if (!resp.ok) {
        setMsg("Could not fetch announcements.");
        setLoading(false);
        return;
      }

      setAnnouncements(Array.isArray(data) ? data : data.results || []);
      setMsg("Announcements fetched successfully.");
    } catch (error) {
      setMsg("Could not fetch announcements.");
    } finally {
      setLoading(false);
    }
  }

  async function fetchEnrollments() {
    setMsg("");
    setLoading(true);

    try {
      const resp = await apiGet("/api/enrollments/", authHeader);
      const data = await resp.json().catch(() => []);

      if (!resp.ok) {
        setMsg("Could not fetch enrollments.");
        setLoading(false);
        return;
      }

      setEnrollments(Array.isArray(data) ? data : data.results || []);
      setMsg("Enrollments fetched successfully.");
    } catch (error) {
      setMsg("Could not fetch enrollments.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        fontFamily: "system-ui, Arial, sans-serif",
        padding: 24,
        maxWidth: 1000,
        margin: "0 auto",
        color: "#111827",
      }}
    >
      <div
        style={{
          background: "#0f172a",
          color: "white",
          padding: 24,
          borderRadius: 16,
          marginBottom: 24,
        }}
      >
        <h1 style={{ margin: 0 }}>Landmine Soft LMS Demo</h1>
        <p style={{ marginTop: 8, opacity: 0.9 }}>
          React frontend connected to your deployed Django backend
        </p>
      </div>

      <div
        style={{
          background: "#ffffff",
          border: "1px solid #e5e7eb",
          borderRadius: 16,
          padding: 20,
          boxShadow: "0 4px 16px rgba(0,0,0,0.05)",
        }}
      >
        <h2 style={{ marginTop: 0 }}>Login</h2>

        <form onSubmit={handleLogin}>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label>Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                style={{ padding: 10, borderRadius: 8, minWidth: 140 }}
              >
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label>Email</label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter email"
                style={{ padding: 10, borderRadius: 8, minWidth: 240 }}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                style={{ padding: 10, borderRadius: 8, minWidth: 240 }}
              />
            </div>
          </div>

          <div style={{ marginTop: 16, display: "flex", gap: 12 }}>
            <button
              type="submit"
              style={{
                padding: "10px 18px",
                borderRadius: 10,
                border: "none",
                background: "#2563eb",
                color: "white",
                cursor: "pointer",
              }}
            >
              {loading ? "Loading..." : "Login"}
            </button>

            <button
              type="button"
              onClick={handleLogout}
              style={{
                padding: "10px 18px",
                borderRadius: 10,
                border: "1px solid #d1d5db",
                background: "#f9fafb",
                cursor: "pointer",
              }}
            >
              Logout
            </button>
          </div>
        </form>
      </div>

      {msg && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            borderRadius: 10,
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
          }}
        >
          {msg}
        </div>
      )}

      {token && (
        <div
          style={{
            marginTop: 20,
            background: "#ffffff",
            border: "1px solid #e5e7eb",
            borderRadius: 16,
            padding: 20,
            boxShadow: "0 4px 16px rgba(0,0,0,0.05)",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Actions</h2>

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button
              onClick={fetchStudentProfile}
              style={buttonStyle}
            >
              Get Profile
            </button>

            <button
              onClick={fetchAnnouncements}
              style={buttonStyle}
            >
              View Announcements
            </button>

            <button
              onClick={fetchEnrollments}
              style={buttonStyle}
            >
              View Enrollments
            </button>
          </div>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: 13, opacity: 0.8 }}>JWT token (truncated)</div>
            <pre
              style={{
                background: "#f8fafc",
                padding: 12,
                borderRadius: 8,
                overflow: "auto",
                border: "1px solid #e5e7eb",
              }}
            >
              {token.slice(0, 80)}...
            </pre>
          </div>
        </div>
      )}

      {profile && (
        <Section title="Student Profile" data={profile} />
      )}

      {announcements.length > 0 && (
        <Section title="Announcements" data={announcements} />
      )}

      {enrollments.length > 0 && (
        <Section title="Enrollments" data={enrollments} />
      )}
    </div>
  );
}

function Section({ title, data }) {
  return (
    <div
      style={{
        marginTop: 20,
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 16,
        padding: 20,
        boxShadow: "0 4px 16px rgba(0,0,0,0.05)",
      }}
    >
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <pre
        style={{
          background: "#f8fafc",
          padding: 12,
          borderRadius: 8,
          overflow: "auto",
          border: "1px solid #e5e7eb",
        }}
      >
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}

const buttonStyle = {
  padding: "10px 18px",
  borderRadius: 10,
  border: "none",
  background: "#111827",
  color: "white",
  cursor: "pointer",
};
