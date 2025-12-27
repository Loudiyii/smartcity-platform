import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForgotPassword } from '../hooks/useAuth'

export default function ForgotPassword() {
  const { mutate: sendResetEmail, isPending, isSuccess, error } = useForgotPassword()

  const [email, setEmail] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendResetEmail({ email })
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Mot de passe oublié</h1>
          <p className="text-gray-600">
            Entrez votre email pour recevoir un lien de réinitialisation
          </p>
        </div>

        {!isSuccess ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="marie@example.com"
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                Une erreur est survenue. Veuillez réessayer.
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isPending}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isPending ? 'Envoi en cours...' : 'Envoyer le lien de réinitialisation'}
            </button>
          </form>
        ) : (
          <div className="space-y-6">
            {/* Success Message */}
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
              <p className="font-semibold mb-1">Email envoyé!</p>
              <p className="text-sm">
                Un email de réinitialisation a été envoyé à <strong>{email}</strong>.
                Vérifiez votre boîte de réception et suivez les instructions.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
              <p className="font-semibold mb-1">Vous n'avez pas reçu l'email?</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Vérifiez votre dossier spam/courrier indésirable</li>
                <li>Assurez-vous que l'adresse email est correcte</li>
                <li>Attendez quelques minutes (l'envoi peut prendre du temps)</li>
              </ul>
            </div>
          </div>
        )}

        {/* Back to Login Link */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <Link to="/login" className="text-blue-600 hover:text-blue-700 font-semibold">
            Retour à la connexion
          </Link>
        </div>
      </div>
    </div>
  )
}
