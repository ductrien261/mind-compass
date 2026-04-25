"use client";

import React, { useState, useRef } from 'react';
import { useRouter } from "next/navigation";
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import {
  Brain, ArrowRight, Activity, Smile,
  MessageCircle, Star, Phone, User,
  CheckCircle, Zap, HeartPulse, ChevronRight,
  ShieldCheck, ArrowUpRight
} from 'lucide-react';

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const yBg = useTransform(scrollYProgress, [0, 1], ['0%', '20%']);
  const router = useRouter();

  const wowContainerRef = useRef(null);
  const { scrollYProgress: wowProgress } = useScroll({
    target: wowContainerRef,
    offset: ["start center", "end center"]
  });

  return (
    <div className="font-sans text-slate-900 bg-[#FAFAFA] min-h-screen overflow-hidden selection:bg-blue-200">

      {/* 1. NAVBAR */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 md:px-12 bg-[#FAFAFA]/80 backdrop-blur-md border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-600 font-extrabold text-2xl tracking-tighter">
            MindCompass<span className="text-orange-500">.</span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-semibold text-slate-500">
            <a href="#" className="hover:text-blue-600 transition-colors">Tính năng</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Phương pháp</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Câu hỏi thường gặp</a>
          </div>
          <button onClick={() => router.push("/assess")} className="bg-blue-600 text-white px-6 py-2.5 rounded-full font-semibold text-sm hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-500/30">
            Làm bài Test
          </button>
        </div>
      </nav>

      {/* 2. HERO SECTION (Floating UI Style) */}
      <section className="relative pt-32 pb-20 px-6 md:px-12 max-w-7xl mx-auto flex flex-col lg:flex-row items-center min-h-[90vh]">

        {/* Left Content */}
        <div className="w-full lg:w-1/2 z-10 relative mt-10 lg:mt-0 text-center lg:text-left">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 text-orange-500 font-bold mb-6 text-sm uppercase tracking-wider"
          >
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-extrabold text-slate-900 mb-6 leading-[1.1] tracking-tight"
          >
            Lắng Nghe <br />
            <span className="text-blue-600">Sức Khỏe Tinh Thần</span> <br />
            Của Bạn 🎉
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-slate-500 mb-10 max-w-md mx-auto lg:mx-0 leading-relaxed font-medium"
          >
            Nếu bạn cảm thấy căng thẳng, lo âu, hoặc đơn giản là muốn hiểu rõ hơn về tâm trí mình, hãy bắt đầu chia sẻ ngay tại đây.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start"
          >
            <button
              onClick={() => router.push("/assess")}
              className="bg-blue-600 text-white px-8 py-4 rounded-full text-lg font-bold hover:bg-blue-700 transition-all hover:scale-105 shadow-[0_8px_30px_rgb(37,99,235,0.3)] w-full sm:w-auto">
              Bắt đầu đánh giá
            </button>
            <button className="px-8 py-4 rounded-full text-lg font-bold text-slate-600 hover:bg-slate-100 transition-all w-full sm:w-auto flex items-center justify-center gap-2">
              Tìm hiểu thêm <ArrowRight size={20} />
            </button>
          </motion.div>
        </div>

        {/* Right Content - Floating UI Cards */}
        <div className="w-full lg:w-1/2 h-125 lg:h-150 relative mt-16 lg:mt-0 hidden md:block">
          {/* Main Central Card */}
          <motion.div
            animate={{ y: [-10, 10, -10] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 bg-white p-6 rounded-4xl shadow-2xl border border-slate-100 z-20"
          >
            <div className="w-full h-48 bg-orange-100 rounded-2xl mb-6 flex items-center justify-center relative overflow-hidden">
              <Smile size={80} className="text-orange-400" />
              {/* Decorative blobs */}
              <div className="absolute top-0 right-0 w-20 h-20 bg-orange-200 rounded-full blur-xl opacity-50"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-yellow-200 rounded-full blur-xl opacity-50"></div>
            </div>
            <h3 className="font-bold text-xl text-center mb-2">Đang phân tích...</h3>
            <div className="flex gap-2 justify-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </motion.div>

          {/* Floating Element 1 - DASS Score */}
          <motion.div
            animate={{ y: [0, -20, 0], rotate: [-2, 2, -2] }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            className="absolute top-10 right-10 bg-white p-4 rounded-2xl shadow-xl flex items-center gap-4 border border-slate-50 z-30"
          >
            <div className="w-12 h-12 bg-pink-100 text-pink-500 rounded-full flex items-center justify-center">
              <HeartPulse size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-400 font-bold uppercase">Nhịp độ cảm xúc</p>
              <p className="font-extrabold text-lg">Ổn định</p>
            </div>
          </motion.div>

          {/* Floating Element 2 - Connection */}
          <motion.div
            animate={{ y: [0, 20, 0], x: [0, -10, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
            className="absolute bottom-20 left-4 bg-white p-4 rounded-2xl shadow-xl border border-slate-50 z-30 flex items-center gap-3"
          >
            <div className="flex -space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-200 border-2 border-white flex items-center justify-center font-bold text-blue-600 text-xs">AI</div>
              <div className="w-10 h-10 rounded-full bg-orange-200 border-2 border-white flex items-center justify-center font-bold text-orange-600 text-xs">You</div>
            </div>
            <div className="text-sm font-bold text-slate-700">Tương tác 1:1</div>
          </motion.div>

          {/* Floating Element 3 - Small badges */}
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/4 left-10 w-12 h-12 bg-yellow-400 rounded-2xl rotate-12 shadow-lg flex items-center justify-center z-10"
          >
            <Star className="text-white" fill="currentColor" size={24} />
          </motion.div>

          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 2 }}
            className="absolute bottom-1/3 right-4 w-14 h-14 bg-purple-500 rounded-full shadow-lg flex items-center justify-center z-10"
          >
            <Brain className="text-white" size={28} />
          </motion.div>

          {/* Background Grid Lines */}
          <svg className="absolute inset-0 w-full h-full z-0 opacity-20" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" className="text-slate-400" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
      </section>

      {/* 3. MOOD SECTION (Know your mood) */}
      <section className="py-24 px-6 bg-white border-y border-slate-100">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-16 gap-8">
            <div>
              <div className="flex items-center gap-2 text-orange-500 font-bold mb-4">
                <Smile size={20} /> Mood
              </div>
              <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 leading-tight">
                Nhận biết <br /><span className="text-blue-600">tâm trạng</span> của bạn
              </h2>
            </div>
            <a href="#" className="flex items-center gap-2 text-blue-600 font-bold hover:text-blue-800 transition-colors">
              Tìm hiểu thêm <ChevronRight size={20} />
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="group">
              <div className="text-7xl mb-6 transition-transform group-hover:scale-110 group-hover:-rotate-6 origin-bottom-left">😔</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Trầm cảm</h3>
              <p className="text-slate-500 font-medium leading-relaxed">Bạn cảm thấy trống rỗng, mất đi niềm vui và hứng thú với những điều mình từng yêu thích.</p>
            </div>
            <div className="group">
              <div className="text-7xl mb-6 transition-transform group-hover:scale-110 origin-bottom">😰</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Lo âu</h3>
              <p className="text-slate-500 font-medium leading-relaxed">Bạn thường xuyên cảm thấy bồn chồn, tay chân run rẩy và lo sợ những điều mơ hồ.</p>
            </div>
            <div className="group">
              <div className="text-7xl mb-6 transition-transform group-hover:scale-110 group-hover:rotate-6 origin-bottom-right">😫</div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">Căng thẳng</h3>
              <p className="text-slate-500 font-medium leading-relaxed">Bạn dễ bị kích động, khó thư giãn và cảm thấy quá tải với áp lực xung quanh.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS (The WOW Sticky Scroll) */}
      <section ref={wowContainerRef} className="py-32 px-6 bg-slate-900 text-white relative">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-16">

          {/* Left Sticky Title */}
          <div className="w-full lg:w-1/3 lg:sticky lg:top-32 h-fit mb-12 lg:mb-0">
            <div className="inline-flex items-center gap-2 text-teal-400 font-bold mb-4 uppercase tracking-wider text-sm">
              <Zap size={16} /> Hoạt động như thế nào?
            </div>
            <h2 className="text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
              Trải nghiệm <br />thấu cảm,<br /> không áp lực.
            </h2>
            <p className="text-slate-400 font-medium text-lg">
              Hệ thống được thiết kế để lắng nghe bạn từng bước một, như một người bạn đồng hành.
            </p>
          </div>

          {/* Right Scrollable Cards */}
          <div className="w-full lg:w-2/3 space-y-24">

            {/* Card 1 */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ margin: "-100px" }}
              className="bg-linear-to-br from-slate-800 to-slate-800/50 p-8 md:p-12 rounded-[2.5rem] border border-slate-700 relative overflow-hidden group"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-blue-500/30 transition-colors"></div>
              <div className="text-6xl font-black text-slate-700 mb-6">01</div>
              <h3 className="text-3xl font-bold mb-4">Sàng lọc 1 phút</h3>
              <p className="text-slate-300 text-lg leading-relaxed mb-8">
                Bắt đầu nhẹ nhàng với 6 câu hỏi cốt lõi để nhận diện sơ bộ cảm xúc của bạn. Không cần điền form dài dòng, chỉ cần bấm chọn cảm giác của mình.
              </p>
              <div className="bg-slate-900/50 p-4 rounded-2xl flex items-center gap-4 border border-slate-700/50">
                <div className="w-12 h-12 bg-blue-500/20 text-blue-400 rounded-xl flex items-center justify-center"><CheckCircle size={24} /></div>
                <div>
                  <p className="font-bold">Nhanh chóng & Bí mật</p>
                  <p className="text-sm text-slate-400">Không lưu thông tin định danh</p>
                </div>
              </div>
            </motion.div>

            {/* Card 2 */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ margin: "-100px" }}
              className="bg-linear-to-br from-slate-800 to-slate-800/50 p-8 md:p-12 rounded-[2.5rem] border border-slate-700 relative overflow-hidden group"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-orange-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-orange-500/30 transition-colors"></div>
              <div className="text-6xl font-black text-slate-700 mb-6">02</div>
              <h3 className="text-3xl font-bold mb-4">Hỏi đáp chuyên sâu</h3>
              <p className="text-slate-300 text-lg leading-relaxed mb-8">
                Nếu phát hiện những vướng mắc sâu hơn, AI sẽ chủ động đặt thêm các câu hỏi tập trung vào vấn đề đó, giống như cách một bác sĩ tâm lý đặt câu hỏi.
              </p>
              <div className="bg-slate-900/50 p-4 rounded-2xl flex items-center gap-4 border border-slate-700/50">
                <div className="w-12 h-12 bg-orange-500/20 text-orange-400 rounded-xl flex items-center justify-center"><Brain size={24} /></div>
                <div>
                  <p className="font-bold">Linh hoạt theo từng người</p>
                  <p className="text-sm text-slate-400">Câu hỏi thay đổi dựa trên câu trả lời trước</p>
                </div>
              </div>
            </motion.div>

            {/* Card 3 */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ margin: "-100px" }}
              className="bg-linear-to-br from-slate-800 to-slate-800/50 p-8 md:p-12 rounded-[2.5rem] border border-slate-700 relative overflow-hidden group"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-teal-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-teal-500/30 transition-colors"></div>
              <div className="text-6xl font-black text-slate-700 mb-6">03</div>
              <h3 className="text-3xl font-bold mb-4">Nhận Báo cáo & Lời khuyên</h3>
              <p className="text-slate-300 text-lg leading-relaxed mb-8">
                Xem kết quả phân tích đa chiều về phổ cảm xúc của bạn. Nhận các bài tập chữa lành (hít thở, viết nhật ký) hoặc lời khuyên chuyên môn phù hợp nhất.
              </p>
              <div className="bg-slate-900/50 p-4 rounded-2xl flex items-center gap-4 border border-slate-700/50">
                <div className="w-12 h-12 bg-teal-500/20 text-teal-400 rounded-xl flex items-center justify-center"><Activity size={24} /></div>
                <div>
                  <p className="font-bold">Giải pháp thực tế</p>
                  <p className="text-sm text-slate-400">Dễ dàng áp dụng vào cuộc sống</p>
                </div>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* 5. SCIENCE & TECH (Explain DASS & MINI simply) */}
      <section className="py-24 px-6 bg-blue-50/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-slate-900 mb-4">Cách chúng tôi thấu hiểu bạn</h2>
            <p className="text-slate-500 font-medium text-lg max-w-2xl mx-auto">
              Chúng tôi số hóa các công cụ y khoa quốc tế thành một trải nghiệm tương tác tự nhiên, giúp bạn có kết quả chính xác mà không cảm thấy nặng nề.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* DASS-42 Card */}
            <div className="bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-sm hover:shadow-xl transition-shadow relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-100 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
              <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-8">
                <Activity size={32} />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-4">Thang đo DASS-42</h3>
              <p className="text-slate-600 leading-relaxed mb-6">
                Là bộ câu hỏi được công nhận toàn cầu trong tâm lý học lâm sàng. DASS-42 giúp định lượng chính xác sự thay đổi của 3 nhóm cảm xúc: <strong>Trầm cảm (Depression)</strong>, <strong>Lo âu (Anxiety)</strong> và <strong>Căng thẳng (Stress)</strong>.
              </p>
              <ul className="space-y-3 text-slate-500 font-medium">
                <li className="flex items-center gap-3"><CheckCircle size={18} className="text-blue-500" /> Xác định mức độ (Nhẹ, Vừa, Nặng)</li>
                <li className="flex items-center gap-3"><CheckCircle size={18} className="text-blue-500" /> Đánh giá tổng quan phổ cảm xúc</li>
              </ul>
            </div>

            {/* M.I.N.I Card */}
            <div className="bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-sm hover:shadow-xl transition-shadow relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-orange-100 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2"></div>
              <div className="w-16 h-16 bg-orange-100 text-orange-600 rounded-2xl flex items-center justify-center mb-8">
                <MessageCircle size={32} />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-4">Bộ phỏng vấn M.I.N.I</h3>
              <p className="text-slate-600 leading-relaxed mb-6">
                M.I.N.I (Mini International Neuropsychiatric Interview) đóng vai trò như một chuyên gia. AI sẽ sử dụng bộ câu hỏi này để <strong>đào sâu (Rẽ nhánh)</strong> vào các rối loạn cụ thể (như Rối loạn hoảng sợ, GAD) nếu nhận thấy dấu hiệu rủi ro.
              </p>
              <ul className="space-y-3 text-slate-500 font-medium">
                <li className="flex items-center gap-3"><CheckCircle size={18} className="text-orange-500" /> Tương tác linh hoạt theo câu trả lời</li>
                <li className="flex items-center gap-3"><CheckCircle size={18} className="text-orange-500" /> Nhận diện chuyên sâu các rối loạn cụ thể</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 6. FOOTER */}
      <footer className="bg-white pt-24 pb-12 px-6 border-t border-slate-100">
        <div className="max-w-7xl mx-auto">
          {/* Top Footer CTA */}
          <div className="bg-blue-600 rounded-[3rem] p-12 text-center text-white mb-20 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
            <h2 className="text-4xl md:text-5xl font-extrabold mb-6 relative z-10">Sẵn sàng thấu hiểu bản thân?</h2>
            <p className="text-blue-100 text-lg mb-8 relative z-10 max-w-2xl mx-auto">Chỉ mất 2 phút. An toàn, bảo mật và hoàn toàn miễn phí.</p>
            <button className="bg-white text-blue-600 px-8 py-4 rounded-full text-lg font-bold hover:bg-slate-50 transition-all hover:scale-105 shadow-xl relative z-10">
              Bắt đầu bài kiểm tra ngay
            </button>
          </div>

          {/* Bottom Footer Links */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 text-blue-600 font-extrabold text-2xl tracking-tighter mb-6">
                MindCompass<span className="text-orange-500">.</span>
              </div>
              <p className="text-slate-500 font-medium leading-relaxed max-w-sm">
                Ứng dụng công nghệ AI và hệ chuyên gia để mang lại giải pháp chăm sóc sức khỏe tinh thần hiện đại, thân thiện cho mọi người.
              </p>
            </div>

            <div>
              <h4 className="font-bold text-slate-900 mb-6 uppercase tracking-wider text-sm">Về chúng tôi</h4>
              <ul className="space-y-4 text-slate-500 font-medium">
                <li><a href="#" className="hover:text-blue-600 transition-colors">Tính năng hệ thống</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Phương pháp khoa học</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Đội ngũ chuyên gia</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-slate-900 mb-6 uppercase tracking-wider text-sm">Hỗ trợ</h4>
              <ul className="space-y-4 text-slate-500 font-medium">
                <li><a href="#" className="hover:text-blue-600 transition-colors">Câu hỏi thường gặp</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Chính sách bảo mật</a></li>
                <li><a href="#" className="hover:text-blue-600 transition-colors">Điều khoản sử dụng</a></li>
              </ul>
            </div>
          </div>

          {/* Copyright & Disclaimer */}
          <div className="border-t border-slate-100 pt-8 flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-slate-400 font-medium">
            <p>© 2026 MindCompass. All rights reserved.</p>
            <div className="bg-slate-50 px-4 py-3 rounded-xl max-w-xl text-center md:text-right border border-slate-100 flex items-start gap-3">
              <ShieldCheck size={20} className="text-slate-400 shrink-0 mt-0.5" />
              <p>MindCompass là công cụ hỗ trợ nhận thức dựa trên DASS-42 và M.I.N.I. Kết quả từ hệ thống không nhằm mục đích thay thế chẩn đoán y tế chuyên nghiệp.</p>
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
}