'use client'

import { useState } from 'react'
import axios from 'axios'

const questions = [
  "Мало интереса или удовольствия от занятий",
  "Чувство подавленности, депрессии или безнадёжности",
  "Трудности с засыпанием, сном или, наоборот, слишком долгий сон",
  "Чувство усталости или нехватки энергии",
  "Потеря аппетита или переедание",
  "Низкая самооценка, чувство вины или никчемности",
  "Трудности с концентрацией внимания",
  "Медлительность или чрезмерная суетливость, замеченные другими",
  "Мысли о смерти или причинении себе вреда"
]

const options = [
  { label: "Совсем нет", value: 0 },
  { label: "Несколько дней", value: 1 },
  { label: "Больше половины дней", value: 2 },
  { label: "Почти каждый день", value: 3 }
]

export default function PHQ9Form() {
  const [answers, setAnswers] = useState<number[]>(Array(9).fill(0))
  const [submitted, setSubmitted] = useState(false)

  const handleChange = (index: number, value: number) => {
    const updated = [...answers]
    updated[index] = value
    setAnswers(updated)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8000/survay', { answers })
      setSubmitted(true)
    } catch (err) {
      alert('Ошибка при отправке данных')
      console.error(err)
    }
  }

  if (submitted) return <p>Спасибо за прохождение опроса!</p>

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Опрос PHQ-9</h1>
      {questions.map((q, i) => (
        <div key={i} className="mb-4">
          <p className="font-medium">{i + 1}. {q}</p>
          <div className="space-x-4">
            {options.map((opt) => (
              <label key={opt.value}>
                <input
                  type="radio"
                  name={`q${i}`}
                  value={opt.value}
                  checked={answers[i] === opt.value}
                  onChange={() => handleChange(i, opt.value)}
                  required
                />
                {" "}{opt.label}
              </label>
            ))}
          </div>
        </div>
      ))}
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Отправить
      </button>
    </form>
  )
}
