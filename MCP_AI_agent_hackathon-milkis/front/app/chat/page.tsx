'use client'
import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import Link from 'next/link'

export default function ChatPage({ params }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [chatId, setChatId] = useState('')
  const messagesEndRef = useRef(null)

  // Инициализация чата при загрузке
  useEffect(() => {
    const newChatId = params.chatId || generateChatId()
    setChatId(newChatId)

    // Загрузка истории чата, если есть
    loadChatHistory(newChatId)
  }, [params.chatId])

  const generateChatId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  const loadChatHistory = async (id) => {
    try {
      // Здесь можно добавить загрузку истории с сервера
      const welcomeMessage = { text: "Привет! Я твой психологический помощник. Расскажи, как ты себя чувствуешь?", sender: 'bot' }
      setMessages([welcomeMessage])
    } catch (err) {
      console.error('Ошибка загрузки истории:', err)
    }
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = { text: input, sender: 'user', chat_id: chatId }
    setMessages(prev => [...prev, userMessage])
    setInput('')

    try {
      const response = await axios.post('http://localhost:8001/api/chat', userMessage)
      setMessages(prev => [...prev, response.data])
    } catch (err) {
      console.error('Ошибка чата:', err)
      setMessages(prev => [...prev, {
        text: 'Ошибка соединения с сервером',
        sender: 'bot'
      }])
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Чат поддержки</h1>
        <Link href="/" className="text-blue-600 hover:underline">
          ← Назад к опросу
        </Link>
      </div>

      <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-3 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}
          >
            <div className={`inline-block px-4 py-2 rounded-lg ${
              msg.sender === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1 border rounded-lg px-4 py-2"
          placeholder="Введите сообщение..."
        />
        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Отправить
        </button>
      </div>
    </div>
  )
}
