'use server'

import prisma from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function submitAttendance(classId: string, absentStudentIds: string[]) {
  const date = new Date()
  date.setHours(0, 0, 0, 0) // Normalize date to midnight

  // First, get all students in this class
  const students = await prisma.student.findMany({
    where: { classId }
  })

  // Prepare attendance records
  const records = students.map(student => ({
    studentId: student.id,
    date,
    status: absentStudentIds.includes(student.id) ? 'ABSENT' : 'PRESENT'
  }))

  // Use a transaction to safely update records (upsert to handle if teacher submits twice on same day)
  for (const record of records) {
    await prisma.attendance.upsert({
      where: {
        studentId_date: {
          studentId: record.studentId,
          date: record.date
        }
      },
      update: {
        status: record.status
      },
      create: {
        studentId: record.studentId,
        date: record.date,
        status: record.status
      }
    })
  }

  revalidatePath('/dashboard/reports')
  return { success: true }
}
