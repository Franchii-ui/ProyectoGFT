import { useState } from 'react';

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="bg-[#213f7f] text-white">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <a href="/" className="flex items-center">
          <img src="/Logo_GFT.jpg" alt="GFT" className="h-8" />
        </a>
        
        <div className="hidden md:flex items-center space-x-6">
          <a href="#" className="hover:text-gray-300">Historial</a>
          <a href="#" className="hover:text-gray-300">Recientes</a>
          <a href="/login" className="bg-white text-[#213f7f] px-4 py-1 rounded hover:bg-gray-100">
            Iniciar Sesión
          </a>
        </div>
        
        <button 
          className="md:hidden focus:outline-none" 
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          ☰
        </button>
      </div>
      
      {isMenuOpen && (
        <div className="md:hidden px-4 pb-3 space-y-3">
          <a href="#" className="block hover:bg-blue-700 px-2 py-1 rounded">Historial</a>
          <a href="#" className="block hover:bg-blue-700 px-2 py-1 rounded">Recientes</a>
          <a href="/login" className="block bg-white text-[#213f7f] px-2 py-1 rounded mt-2">
            Iniciar Sesión
          </a>
        </div>
      )}
    </nav>
  );
}