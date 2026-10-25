'use client'

import { useEffect, useState } from "react"
import QRCode from "qrcode"

export default function QRCodeDisplay({ text }: { text: string }) {
  const [src, setSrc] = useState('')

  useEffect(() => {
    QRCode.toDataURL(text, { width: 200, margin: 1, color: { dark: '#0f172a', light: '#ffffff' } })
      .then(url => setSrc(url))
      .catch(err => console.error(err))
  }, [text])

  if (!src) return <div className="w-[200px] h-[200px] bg-gray-100 animate-pulse rounded-lg flex items-center justify-center text-gray-400 text-sm">جاري التوليد...</div>

  return <img src={src} alt="QR Code" className="w-[200px] h-[200px] rounded-lg shadow-sm border border-gray-200" />
}
