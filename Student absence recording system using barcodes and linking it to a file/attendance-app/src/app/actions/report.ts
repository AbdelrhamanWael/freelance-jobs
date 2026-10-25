'use server'

import prisma from '@/lib/prisma'

export async function getStudentsReport() {
  const students = await prisma.student.findMany({
    include: {
      class: true,
      attendances: {
        where: {
          status: 'ABSENT'
        }
      }
    },
    orderBy: {
      classId: 'asc'
    }
  })

  // To calculate percentage, we need the total number of school days recorded for each class
  // For simplicity, we can get the total unique dates an attendance was recorded for a class
  const classDays = await prisma.attendance.groupBy({
    by: ['date'],
    _count: true
  })
  const totalDaysRecorded = classDays.length > 0 ? classDays.length : 1 // Avoid division by zero

  const report = students.map(student => {
    const absentDays = student.attendances.length
    const presentDays = totalDaysRecorded - absentDays
    const absencePercentage = ((absentDays / totalDaysRecorded) * 100).toFixed(1)

    return {
      id: student.id,
      name: student.name,
      className: student.class.name,
      absentDays,
      presentDays,
      absencePercentage: Number(absencePercentage),
      totalDays: totalDaysRecorded,
      absentDates: student.attendances.map(a => a.date)
    }
  })

  return report
}
