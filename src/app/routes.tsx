import { createBrowserRouter } from "react-router-dom";

import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ScanSetup } from "./pages/ScanSetup";
import { ScanProgress } from "./pages/ScanProgress";
import { ScanResults } from "./pages/ScanResults";
import { HistoryPage } from "./pages/HistoryPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/scan",
    element: <ScanSetup />,
  },
  {
    path: "/scanning",
    element: <ScanProgress />,
  },
  {
    path: "/results",
    element: <ScanResults />,
  },
  {
    path: "/history",
    element: <HistoryPage />,
  },
]);
