import Link from "next/link";

export default function Nav() {
  return (
    <nav style={{ display: "flex", gap: "16px", marginBottom: "1rem" }}>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
    </nav>
  );
}
