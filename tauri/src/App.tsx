import { motion, AnimatePresence } from "motion/react";
import {
  Code2,
  Sparkles,
  Zap,
  ArrowRight,
  Github,
  FolderOpen,
  Plus,
  X,
} from "lucide-react";
import { useState } from "react";
import { Spinner } from "@/components/ui/spinner";
import "./App.css";

export default function UnlovableLanding() {
  const [showPopup, setShowPopup] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [projectOpenSuccess, setPOpenSuccess] = useState(false);
  const [openingProject, setOpeningProject] = useState(false);

  async function handleOpenButton() {
    try {
      const dirHandle = await (window as any).showDirectoryPicker();
      setOpeningProject(true);

      const files: Record<string, File> = {};

      for await (const entry of dirHandle.values()) {
        if (entry.kind === "file") {
          files[entry.name] = await entry.getFile();
        }
      }

      // send file metadata to your backend

      setOpeningProject(false);
      setPOpenSuccess(true);
    } catch (err) {
      console.error(err);
      setOpeningProject(false);
    }
  }

  function handleNewProject() {
    setShowInstructions(true);
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute inset-0 opacity-30"
          animate={{
            background: [
              "radial-gradient(circle at 20% 50%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 80% 30%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 20% 70%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 50% 80%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 50% 20%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 20% 50%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
            ],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>

      <div className="relative z-10">
        <nav className="px-6 py-6">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-4xl">💔</span>
              <span className="text-2xl font-bold text-white font-sans">
                unlovable
              </span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/20 transition-all">
                <Github size={20} />
                <span>GitHub</span>
              </button>
            </motion.div>
          </div>
        </nav>

        <div className="max-w-6xl mx-auto px-6 pt-20 pb-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight font-sans">
              Build multi-page apps
              <br />
              <span className="bg-linear-to-r from-pink-400 to-blue-400 bg-clip-text text-transparent">
                with plain text
              </span>
            </h1>
          </motion.div>

          <motion.p
            className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto font-sans"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            No frameworks. No build steps. No complexity. Just describe what you
            want, and unlovable creates beautiful, functional applications
            instantly.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <button
              onClick={() => setShowPopup(true)}
              className="group flex items-center gap-2 px-8 py-4 rounded-xl bg-linear-to-r from-pink-500 to-blue-500 text-white font-semibold hover:shadow-2xl hover:shadow-pink-500/50 transition-all"
            >
              Get Started
              <ArrowRight
                size={20}
                className="group-hover:translate-x-1 transition-transform"
              />
            </button>
            <button className="px-8 py-4 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white font-semibold hover:bg-white/20 transition-all">
              Learn More
            </button>
          </motion.div>
        </div>

        <div className="max-w-6xl mx-auto px-6 pb-32">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Code2,
                title: "Plain Text Input",
                description:
                  "Describe your app in natural language. No code required, no learning curve.",
                delay: 0.2,
              },
              {
                icon: Zap,
                title: "Instant Generation",
                description:
                  "Watch your ideas transform into working applications in seconds, not hours.",
                delay: 0.4,
              },
              {
                icon: Sparkles,
                title: "Multi-Page Magic",
                description:
                  "Create complex, multi-page experiences with routing, state, and navigation.",
                delay: 0.6,
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                className="p-8 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: feature.delay }}
              >
                <div className="w-12 h-12 rounded-lg bg-linear-to-r from-pink-500 to-blue-500 flex items-center justify-center mb-4">
                  <feature.icon className="text-white" size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3 font-sans">
                  {feature.title}
                </h3>
                <p className="text-slate-400 font-sans">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-6 pb-32">
          <motion.div
            className="rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 overflow-hidden"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <div className="bg-white/5 px-6 py-4 border-b border-white/10 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-4 text-slate-400 text-sm font-mono">
                unlovable.txt
              </span>
            </div>
            <div className="p-8 font-mono text-sm text-slate-300 leading-relaxed">
              <div className="text-pink-400 font-mono">
                Create a simple blog app with:
              </div>
              <div className="ml-4 mt-2 font-mono">
                - A home page listing all posts
              </div>
              <div className="ml-4 font-mono">- Individual post pages</div>
              <div className="ml-4 font-mono">- A contact form</div>
              <div className="ml-4 font-mono">- Dark mode toggle</div>
              <div className="mt-4 text-blue-400 font-mono">
                → Done. Your app is ready.
              </div>
            </div>
          </motion.div>
        </div>

        <footer className="border-t border-white/10 bg-white/5 backdrop-blur-md">
          <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">💔</span>
              <span className="text-slate-400">
                Built with heartbreak and AI
              </span>
            </div>
            <div className="flex gap-6 text-slate-400">
              <a href="#" className="hover:text-white transition-colors">
                Docs
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Examples
              </a>
              <a href="#" className="hover:text-white transition-colors">
                GitHub
              </a>
            </div>
          </div>
        </footer>
      </div>

      <AnimatePresence>
        {showPopup && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Backdrop */}
            <motion.div
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => {
                setShowPopup(false);
                setShowInstructions(false);
                setPOpenSuccess(false);
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            <motion.div
              className="relative w-full max-w-md rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-white/20 shadow-2xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              <button
                onClick={() => {
                  setShowPopup(false);
                  setShowInstructions(false);
                  setPOpenSuccess(false);
                }}
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X size={20} className="text-slate-400" />
              </button>

              <div className="p-8">
                <AnimatePresence mode="wait">
                  {!showInstructions ? (
                    <motion.div
                      key="options"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-bold text-white mb-2 font-sans">
                        Get Started
                      </h2>
                      <p className="text-slate-400 mb-8 font-sans">
                        Choose how you'd like to begin
                      </p>

                      <div className="space-y-3">
                        <button
                          onClick={handleOpenButton}
                          className={`w-full flex items-center gap-4 p-6 rounded-xl border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all group ${openingProject && "grayscale"} ${projectOpenSuccess ? "bg-green-700" : "bg-white/5"}`}
                        >
                          {!openingProject && (
                            <div className="w-12 h-12 rounded-lg bg-linear-to-r from-blue-500 to-cyan-500 flex items-center justify-center shrink-0">
                              <FolderOpen size={24} className="text-white" />
                            </div>
                          )}
                          {openingProject && (
                            <div className="w-12 h-12 rounded-lg bg-linear-to-r from-blue-500 to-cyan-500 flex items-center justify-center shrink-0">
                              <Spinner />
                            </div>
                          )}
                          <div className="text-left">
                            <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors font-sans">
                              Open Project
                            </h3>
                          </div>
                        </button>

                        <button
                          onClick={handleNewProject}
                          className="w-full flex items-center gap-4 p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all group"
                        >
                          <div className="w-12 h-12 rounded-lg bg-linear-to-r from-pink-500 to-purple-500 flex items-center justify-center shrink-0">
                            <Plus size={24} className="text-white" />
                          </div>
                          <div className="text-left">
                            <h3 className="text-lg font-semibold text-white group-hover:text-pink-400 transition-colors font-sans">
                              New Project
                            </h3>
                            <p className="text-sm text-slate-400 font-sans">
                              Start a fresh project from scratch
                            </p>
                          </div>
                        </button>
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="instructions"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-bold text-white mb-2 font-sans">
                        Create New Project
                      </h2>
                      <p className="text-slate-400 mb-6 font-sans">
                        Follow these steps to get started
                      </p>

                      <div className="space-y-4 mb-6">
                        {[
                          {
                            step: 1,
                            title: "Create a new folder",
                            description:
                              "Choose a location for your project files",
                            delay: 0.1,
                          },
                          {
                            step: 2,
                            title: "Create an index.txt file",
                            description: "Describe your app in plain text",
                            delay: 0.2,
                          },
                          {
                            step: 3,
                            title: "Define routes",
                            description:
                              "Create folders with index.txts to define routes (i.e., <url>/home, <url>/about)",
                            delay: 0.3,
                          },
                          {
                            step: 4,
                            title: "Run unlovable",
                            description:
                              "Open your folder as a project in unlovable and watch your app come to life",
                            delay: 0.4,
                          },
                        ].map((item) => (
                          <motion.div
                            key={item.step}
                            className="p-4 rounded-lg bg-white/5 border border-white/10"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: item.delay }}
                          >
                            <div className="flex items-start gap-3">
                              <span className="shrink-0 w-6 h-6 rounded-full bg-pink-500 flex items-center justify-center text-white text-sm font-bold">
                                {item.step}
                              </span>
                              <div>
                                <h4 className="text-white font-semibold mb-1 font-sans">
                                  {item.title}
                                </h4>
                                <p className="text-sm text-slate-400 font-sans">
                                  {item.description}
                                </p>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>

                      <motion.button
                        onClick={() => setShowInstructions(false)}
                        className="w-full py-3 rounded-lg bg-linear-to-r from-pink-500 to-purple-500 text-white font-semibold hover:shadow-xl hover:shadow-pink-500/50 transition-all font-sans"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3, delay: 0.4 }}
                      >
                        Got it!
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
