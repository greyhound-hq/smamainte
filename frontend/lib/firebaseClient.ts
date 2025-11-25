import { initializeApp, getApps } from 'firebase/app'
import { getAuth, signInAnonymously } from 'firebase/auth'

function getConfig() {
  // Read from NEXT_PUBLIC_* env vars set in Next.js
  return {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  }
}

export function initFirebase() {
  const config = getConfig()
  if (!getApps().length) {
    // If user didn't set config, we still call initializeApp with an empty object
    // Firebase will throw if required fields are missing when used; this keeps init idempotent.
    try {
      initializeApp(config as any)
    } catch (e) {
      // ignore initialize errors in development if config is missing
      // eslint-disable-next-line no-console
      console.warn('Firebase init warning (continuing):', e)
    }
  }
  return getAuth()
}

export async function signInAnon() {
  const auth = getAuth()
  const cred = await signInAnonymously(auth)
  // getIdToken() is available on the user object
  // token will be a string or undefined
  // @ts-ignore
  const token = await cred.user.getIdToken()
  return token
}

export default { initFirebase, signInAnon }
