"use client";

import { useRouter } from "next/navigation";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";
import { googleLogin } from "../api/authApi";
import { extractErrorMessage } from "@/shared/lib/utils/errorHandler";

interface GoogleSignInButtonProps {
  onError: (message: string) => void;
}

export default function GoogleSignInButton({ onError }: GoogleSignInButtonProps) {
  const router = useRouter();

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      onError("Google sign-in failed, please try again");
      return;
    }

    try {
      await googleLogin(credentialResponse.credential);

      const redirectPath = localStorage.getItem("redirectAfterLogin");
      if (redirectPath) {
        localStorage.removeItem("redirectAfterLogin");
        router.push(redirectPath);
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      onError(extractErrorMessage(err, "Google sign-in failed, please try again"));
    }
  };

  return (
    <div className="flex justify-center">
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={() => onError("Google sign-in failed, please try again")}
        width="384"
      />
    </div>
  );
}
