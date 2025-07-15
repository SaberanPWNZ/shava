import Link from "next/link";

export default function Contact() {
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
          Contact Us
        </h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">
              Get in Touch
            </h2>
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              We&apos;d love to hear from you. Send us a message and we&apos;ll respond as soon as possible.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mr-3">
                  <span className="text-blue-600 dark:text-blue-400">📧</span>
                </div>
                <span className="text-gray-700 dark:text-gray-300">contact@shava.dev</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mr-3">
                  <span className="text-green-600 dark:text-green-400">📱</span>
                </div>
                <span className="text-gray-700 dark:text-gray-300">+1 (555) 123-4567</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mr-3">
                  <span className="text-purple-600 dark:text-purple-400">📍</span>
                </div>
                <span className="text-gray-700 dark:text-gray-300">San Francisco, CA</span>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name
                </label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Your name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email
                </label>
                <input 
                  type="email" 
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="your@email.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Message
                </label>
                <textarea 
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Your message here..."
                ></textarea>
              </div>
              
              <button 
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
              >
                Send Message
              </button>
            </form>
          </div>
        </div>
        
        <div className="mt-8 flex gap-4">
          <Link 
            href="/about" 
            className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            About Us
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