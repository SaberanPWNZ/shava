import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Shava - Next.js App",
  description: "A modern Next.js application with Tailwind CSS and routing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
