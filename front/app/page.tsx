'use client'

import { useState } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'

const questions = [
  "В последнее время вам сложно получать радость от хобби, работы или общения?",
  "Вам кажется, что будущее мрачное и ничего не изменится к лучшему?",
  "Просыпаетесь ли вы среди ночи или слишком рано утром без причины?",
  "Чувствуете ли вы, что даже небольшие нагрузки теперь требуют больших усилий?",
  "Вы стали есть значительно меньше, чем раньше, или вовсе забываете о еде?",
  "Вам кажется, что вы обуза для окружающих или не заслуживаете хорошего отношения?",
  "Вам сложно сосредоточиться на работе, учёбе или даже разговоре?",
  "Окружающие говорили, что вы стали двигаться или говорить медленнее обычного?",
  "Бывало ли, что вы думали о смерти или о том, что «всем было бы лучше без меня»?"
]

const options = [
  { label: "Совсем нет", value: 0 },
  { label: "Иногда", value: 1 },
  { label: "Довольно часто", value: 2 },
  { label: "Почти каждый день", value: 3 }
]

const quotes = [
  "Ты не обязан справляться в одиночку 💙",
  "Просить о помощи — это знак силы, а не слабости 🌱",
  "Твои чувства имеют значение 🌈",
  "Каждый шаг вперёд — это прогресс 🐾",
  "Ты важен и достоин заботы 🧡",
  "Пусть сегодня будет шагом к заботе о себе ☀️",
  "Иногда просто быть — уже достаточно 🌼",
  "Дыши. Ты уже справляешься, и это важно 💫",
  "Ты заслуживаешь поддержки и понимания 💖",
  "Маленькие шаги ведут к большим переменам 🌿"
]

export default function PHQ9Form() {
  const [answers, setAnswers] = useState<number[]>(Array(9).fill(0))
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [submitted, setSubmitted] = useState(false)
  const [direction, setDirection] = useState(0)

  const [quoteMap, setQuoteMap] = useState<{ [key: number]: string }>({})

  const getQuoteForQuestion = (index: number) => {
    if (quoteMap[index]) return quoteMap[index]
    const randomIndex = Math.floor(Math.random() * quotes.length)
    const newQuote = quotes[randomIndex]
    setQuoteMap(prev => ({ ...prev, [index]: newQuote }))
    return newQuote
  }

  const handleChange = (value: number) => {
    const updated = [...answers]
    updated[currentQuestion - 1] = value
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

  if (submitted) return (
    <div className="flex justify-center items-center h-screen bg-gradient-to-b from-purple-100 to-white">
      <p className="text-xl font-semibold text-purple-800">Спасибо за прохождение опроса!</p>
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-purple-100 to-white p-6">
      <form onSubmit={handleSubmit} className="w-full max-w-3xl p-8 bg-white shadow-2xl rounded-3xl space-y-8 text-center">
        {currentQuestion > 0 && (
          <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
            <div
              className="bg-blue-600 h-full transition-all duration-300"
              style={{ width: `${(currentQuestion / questions.length) * 100}%` }}
            />
          </div>
        )}

        {currentQuestion === 0 ? (
          <div className="space-y-6">
            <p className="text-gray-800 text-lg text-left max-w-2xl mx-auto">
              <strong>PHQ-9</strong> — это стандартизированный опросник для оценки симптомов депрессии. Он помогает определить уровень психологического состояния за последние 2 недели.
              <br /><br />
              Пожалуйста, внимательно прочитайте каждый вопрос и выберите вариант ответа, который наиболее точно отражает ваше состояние за последние 14 дней.
            </p>
            <button
              type="button"
              onClick={() => setCurrentQuestion(1)}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Начать →
            </button>
          </div>
        ) : (
          <>
            <div className="text-center text-purple-700 italic text-lg">
              {getQuoteForQuestion(currentQuestion)}
            </div>

            <div className="min-h-[180px] relative">
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentQuestion}
                  initial={{ opacity: 0, x: direction > 0 ? 100 : -100 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: direction > 0 ? -100 : 100 }}
                  transition={{ duration: 0.4 }}
                  className="absolute w-full"
                >
                  <p className="text-xl font-semibold text-purple-700 mb-4">
                    {questions[currentQuestion - 1]}
                  </p>

                  <div className="flex flex-col gap-3 items-start max-w-md mx-auto">
                    {options.map((opt) => (
                      <label key={opt.value} className="flex items-center gap-2 text-left cursor-pointer text-gray-800">
                        <input
                          type="radio"
                          name={`q${currentQuestion}`}
                          value={opt.value}
                          checked={answers[currentQuestion - 1] === opt.value}
                          onChange={() => handleChange(opt.value)}
                          className="accent-blue-600"
                          required
                        />
                        <span>{opt.label}</span>
                      </label>
                    ))}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            <div className="flex justify-between items-center pt-4">
              {currentQuestion > 1 ? (
                <button
                  type="button"
                  onClick={() => {
                    setDirection(-1)
                    setCurrentQuestion((prev) => Math.max(1, prev - 1))
                  }}
                  className="px-4 py-2 rounded text-white bg-blue-500 hover:bg-blue-600"
                >
                  ← Назад
                </button>
              ) : <div></div>}

              {currentQuestion === questions.length ? (
                <button
                  type="submit"
                  className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Отправить
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setDirection(1)
                    setCurrentQuestion((prev) => Math.min(questions.length, prev + 1))
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Вперёд →
                </button>
              )}
            </div>
          </>
        )}
      </form>
    </div>
  )
}
