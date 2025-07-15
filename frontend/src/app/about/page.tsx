import Link from "next/link";

export default function About() {
  return (
    <div className="font-sans min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="max-w-4xl mx-auto">
        <nav className="mb-8">
          <Link 
            href="/" 
            className="text-blue-600 hover:text-blue-800 hover:underline mr-4"
          >
            ← Back to Home
          </Link>
        </nav>
        
        <h1 className="text-4xl font-bold mb-6 text-gray-900 dark:text-white">
          About Us
        </h1>
        
        <div className="prose prose-lg dark:prose-invert">
          <p className="text-lg text-gray-700 dark:text-gray-300 mb-4">
            Welcome to Shava - a modern web application built with Next.js and Tailwind CSS.
          </p>
          
          <p className="text-gray-700 dark:text-gray-300 mb-4">
            This project demonstrates the power of modern web development technologies:
          </p>
          
          <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-6">
            <li>Next.js 15 with App Router for file-based routing</li>
            <li>Tailwind CSS for rapid UI development</li>
            <li>TypeScript for type safety</li>
            <li>Responsive design out of the box</li>
          </ul>
          
          <div className="bg-blue-50 dark:bg-blue-900 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-2 text-blue-900 dark:text-blue-100">
              Key Features
            </h2>
            <p className="text-blue-800 dark:text-blue-200">
              Fast development, excellent SEO, and great developer experience with hot reloading and automatic code splitting.
            </p>
          </div>
        </div>
        
        <div className="mt-8 flex gap-4">
          <Link 
            href="/contact" 
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Contact Us
          </Link>
          <Link 
            href="/" 
            className="border border-gray-300 hover:border-gray-400 text-gray-700 dark:text-gray-300 px-6 py-2 rounded-lg transition-colors"
          >
            Go Home
          </Link>
        </div>
      </main>
    </div>
  );
}