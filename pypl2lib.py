# pypl2lib.py - Classes and functions for accessing functions
# in PL2FileReader.dll
#
# (c) 2016 Plexon, Inc., Dallas, Texas
# www.plexon.com
#
# This software is provided as-is, without any warranty.
# You are free to modify or share this file, provided that the above
# copyright notice is kept intact.

from sys import platform
import pathlib
import warnings

if any(platform.startswith(name) for name in ('linux', 'darwin', 'freebsd')):
    from zugbruecke import CtypesSession

    ctypes = CtypesSession(log_level=100)

elif platform.startswith('win'):
    import ctypes
else:
    raise SystemError('unsupported platform')

import os
import platform


class tm(ctypes.Structure):
    _fields_ = [("tm_sec", ctypes.c_int),
                ("tm_min", ctypes.c_int),
                ("tm_hour", ctypes.c_int),
                ("tm_mday", ctypes.c_int),
                ("tm_mon", ctypes.c_int),
                ("tm_year", ctypes.c_int),
                ("tm_wday", ctypes.c_int),
                ("tm_yday", ctypes.c_int),
                ("tm_isdst", ctypes.c_int)]


class PL2FileInfo(ctypes.Structure):
    _fields_ = [("m_CreatorComment", ctypes.c_char * 256),
                ("m_CreatorSoftwareName", ctypes.c_char * 64),
                ("m_CreatorSoftwareVersion", ctypes.c_char * 16),
                ("m_CreatorDateTime", tm),
                ("m_CreatorDateTimeMilliseconds", ctypes.c_int),
                ("m_TimestampFrequency", ctypes.c_double),
                ("m_NumberOfChannelHeaders", ctypes.c_uint),
                ("m_TotalNumberOfSpikeChannels", ctypes.c_uint),
                ("m_NumberOfRecordedSpikeChannels", ctypes.c_uint),
                ("m_TotalNumberOfAnalogChannels", ctypes.c_uint),
                ("m_NumberOFRecordedAnalogChannels", ctypes.c_uint),
                ("m_NumberOfDigitalChannels", ctypes.c_uint),
                ("m_MinimumTrodality", ctypes.c_uint),
                ("m_MaximumTrodality", ctypes.c_uint),
                ("m_NumberOfNonOmniPlexSources", ctypes.c_uint),
                ("m_Unused", ctypes.c_int),
                ("m_ReprocessorComment", ctypes.c_char * 256),
                ("m_ReprocessorSoftwareName", ctypes.c_char * 64),
                ("m_ReprocessorSoftwareVersion", ctypes.c_char * 16),
                ("m_ReprocessorDateTime", tm),
                ("m_ReprocessorDateTimeMilliseconds", ctypes.c_int),
                ("m_StartRecordingTime", ctypes.c_ulonglong),
                ("m_DurationOfRecording", ctypes.c_ulonglong)]


class PL2AnalogChannelInfo(ctypes.Structure):
    _fields_ = [("m_Name", ctypes.c_char * 64),
                ("m_Source", ctypes.c_uint),
                ("m_Channel", ctypes.c_uint),
                ("m_ChannelEnabled", ctypes.c_uint),
                ("m_ChannelRecordingEnabled", ctypes.c_uint),
                ("m_Units", ctypes.c_char * 16),
                ("m_SamplesPerSecond", ctypes.c_double),
                ("m_CoeffToConvertToUnits", ctypes.c_double),
                ("m_SourceTrodality", ctypes.c_uint),
                ("m_OneBasedTrode", ctypes.c_ushort),
                ("m_OneBasedChannelInTrode", ctypes.c_ushort),
                ("m_NumberOfValues", ctypes.c_ulonglong),
                ("m_MaximumNumberOfFragments", ctypes.c_ulonglong)]


class PL2SpikeChannelInfo(ctypes.Structure):
    _fields_ = [("m_Name", ctypes.c_char * 64),
                ("m_Source", ctypes.c_uint),
                ("m_Channel", ctypes.c_uint),
                ("m_ChannelEnabled", ctypes.c_uint),
                ("m_ChannelRecordingEnabled", ctypes.c_uint),
                ("m_Units", ctypes.c_char * 16),
                ("m_SamplesPerSecond", ctypes.c_double),
                ("m_CoeffToConvertToUnits", ctypes.c_double),
                ("m_SamplesPerSpike", ctypes.c_uint),
                ("m_Threshold", ctypes.c_int),
                ("m_PreThresholdSamples", ctypes.c_uint),
                ("m_SortEnabled", ctypes.c_uint),
                ("m_SortMethod", ctypes.c_uint),
                ("m_NumberOfUnits", ctypes.c_uint),
                ("m_SortRangeStart", ctypes.c_uint),
                ("m_SortRangeEnd", ctypes.c_uint),
                ("m_UnitCounts", ctypes.c_ulonglong * 256),
                ("m_SourceTrodality", ctypes.c_uint),
                ("m_OneBasedTrode", ctypes.c_ushort),
                ("m_OneBasedChannelInTrode", ctypes.c_ushort),
                ("m_NumberOfSpikes", ctypes.c_ulonglong)]


class PL2DigitalChannelInfo(ctypes.Structure):
    _fields_ = [("m_Name", ctypes.c_char * 64),
                ("m_Source", ctypes.c_uint),
                ("m_Channel", ctypes.c_uint),
                ("m_ChannelEnabled", ctypes.c_uint),
                ("m_ChannelRecordingEnabled", ctypes.c_uint),
                ("m_NumberOfEvents", ctypes.c_ulonglong)]


class PyPL2FileReader:
    def __init__(self, pl2_dll_path=None):
        """
        PyPL2FileReader class implements functions in the C++ PL2 File Reader
        API provided by Plexon, Inc.
        
        Args:
            pl2_dll_path - path where PL2FileReader.dll is location.
                The default value assumes the .dll files are located in the
                'bin' directory, which is a subdirectory of the directory this
                script is in.
                Any file path passed is converted to an absolute path and checked
                to see if the .dll exists there.
        
        Returns:
            None
        """
        self.file_handle = ctypes.c_int(0)
        if pl2_dll_path is None:
            pl2_dll_path = os.path.join(os.path.split(__file__)[0], 'bin')
        self.pl2_dll_path = os.path.abspath(pl2_dll_path)

        # use default '32bit' dll version
        self.pl2_dll_file = os.path.join(self.pl2_dll_path, 'PL2FileReader.dll')

        try:
            self.pl2_dll = ctypes.CDLL(self.pl2_dll_file)
        except IOError:
            raise IOError("Error: Can't load PL2FileReader.dll at: " + self.pl2_dll_file +
                          "PL2FileReader.dll is bundled with the C++ PL2 Offline Files SDK"
                          "located on the Plexon Inc website: www.plexon.com"
                          "Contact Plexon Support for more information: support@plexon.com")

    def pl2_open_file(self, pl2_file):
        """
        Opens and returns a handle to a PL2 file.
        
        Args:
            pl2_file - full path of the file
            
        Returns:
            file_handle > 0 if success
            file_handle = 0 if failure
            
        """
        if isinstance(pl2_file, pathlib.Path):
            pl2_file = str(pl2_file)
        self.pl2_dll.PL2_OpenFile.argtypes = (
            ctypes.POINTER(ctypes.c_char),
            ctypes.POINTER(ctypes.c_int),
        )
        self.pl2_dll.PL2_OpenFile.memsync = [
            {
                'p': [0],  # ctypes.POINTER argument
                'n': True,  # null-terminated string flag
            }
        ]

        result = self.pl2_dll.PL2_OpenFile(
            pl2_file.encode('ascii'),
            ctypes.byref(self.file_handle),
        )

        # check if spiking data can be loaded using zugbruecke
        self._check_spike_channel_data_consistency()

        return self.file_handle.value

    def pl2_close_file(self):
        """
        Closes handle to PL2 file.

        Returns:
            None
        """

        self.pl2_dll.PL2_CloseFile.argtypes = (
            ctypes.POINTER(ctypes.c_int),
        )
        self.pl2_dll.PL2_CloseFile(ctypes.c_int(1))

    def pl2_close_all_files(self):
        """
        Closes all files that have been opened by the .dll
        
        Args:
            None
        
        Returns:
            None
        """

        self.pl2_dll.PL2_CloseAllFiles.argtypes = ()
        self.pl2_dll.PL2_CloseAllFiles()

    def pl2_get_last_error(self, buffer, buffer_size):
        """
        Retrieve description of the last error
        
        Args:
            buffer - instance of ctypes.c_char array
            buffer_size - size of buffer
        
        Returns:
            1 - Success
            0 - Failure
            buffer is filled with error message
        """

        self.pl2_dll.PL2_GetLastError.argtypes = (
            ctypes.POINTER(ctypes.c_char),
            ctypes.c_int,
        )
        self.pl2_dll.PL2_GetLastError.memsync = [
            {
                'p': [0],
                'l': [1],
                't': ctypes.c_char
            }
        ]

        result = self.pl2_dll.PL2_GetLastError(buffer,
                                                    ctypes.c_int(buffer_size))

        return result

    def _check_spike_channel_data_consistency(self):
        """
        Check if all spiking channels use the same number of samples per
        waveform. Only in this case can zugbruecke reliably load spiking data
        """

        file_info = PL2FileInfo()
        self.pl2_get_file_info(file_info)

        if not file_info.m_TotalNumberOfSpikeChannels:
            return

        # extract samples per spike of first channel
        channel_info = PL2SpikeChannelInfo()
        self.pl2_get_spike_channel_info(0, channel_info)
        n_samples_per_spike = channel_info.m_SamplesPerSpike

        # compare with all other channels
        for i in range(1, file_info.m_TotalNumberOfSpikeChannels):
            channel_info = PL2SpikeChannelInfo()
            self.pl2_get_spike_channel_info(i, channel_info)

            if channel_info.m_SamplesPerSpike != n_samples_per_spike:
                warnings.warn('The spike channels contain different number of samples per spike. '
                              'Spiking data can probably not be loaded using zugbruecke. '
                              'Use a windows operating system or remove the offending channels '
                              'from the file.')
                return

    def pl2_get_file_info(self, pl2_file_info):
        """
        Retrieve information about pl2 file.
        
        Args:
            pl2_file_info - PL2FileInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2FileInfo passed to function is filled with file info
        """

        self.pl2_dll.PL2_GetFileInfo.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(PL2FileInfo),
        )

        result = self.pl2_dll.PL2_GetFileInfo(self.file_handle, ctypes.byref(pl2_file_info))

        return result

    def pl2_get_analog_channel_info(self, zero_based_channel_index, pl2_analog_channel_info):
        """
        Retrieve information about an analog channel
        
        Args:
            zero_based_channel_index - zero-based analog channel index
            pl2_analog_channel_info - PL2AnalogChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2AnalogChannelInfo passed to function is filled with channel info
        """

        self.pl2_dll.PL2_GetAnalogChannelInfo.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(PL2AnalogChannelInfo),
        )

        result = self.pl2_dll.PL2_GetAnalogChannelInfo(self.file_handle,
                                                            ctypes.c_int(zero_based_channel_index),
                                                            ctypes.byref(pl2_analog_channel_info))

        return result

    def pl2_get_analog_channel_info_by_name(self, channel_name, pl2_analog_channel_info):
        """
        Retrieve information about an analog channel
        
        Args:
            channel_name - analog channel name
            pl2_analog_channel_info - PL2AnalogChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure        
            The instance of PL2AnalogChannelInfo is filled with channel info
        """

        self.pl2_dll.PL2_GetAnalogChannelInfoByName.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char),
            ctypes.POINTER(PL2AnalogChannelInfo),
        )

        self.pl2_dll.PL2_GetAnalogChannelInfoByName.memsync = [
            {
                'p': [1],
                'n': True,  # null-terminated string flag
            }
        ]

        if hasattr(channel_name, 'encode'):
            channel_name = channel_name.encode('ascii')

        result = self.pl2_dll.PL2_GetAnalogChannelInfoByName(self.file_handle,
                                                                  channel_name,
                                                                  ctypes.byref(pl2_analog_channel_info))

        return result

    def pl2_get_analog_channel_info_by_source(self, source_id, one_based_channel_index_in_source,
                                              pl2_analog_channel_info):
        """
        Retrieve information about an analog channel
        
        Args:
            file_handle - file handle
            source_id - numeric source ID
            one_based_channel_index_in_source - one-based channel index within the source
            pl2_analog_channel_info - PL2AnalogChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure        
            The instance of PL2AnalogChannelInfo is filled with channel info
        """

        self.pl2_dll.PL2_GetAnalogChannelInfoBySource.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(PL2AnalogChannelInfo),
        )

        result = self.pl2_dll.PL2_GetAnalogChannelInfoBySource(
            self.file_handle,
            ctypes.c_int(source_id),
            ctypes.c_int(one_based_channel_index_in_source),
            ctypes.byref(pl2_analog_channel_info))

        return result

    def pl2_get_analog_channel_data(self, zero_based_channel_index, num_fragments_returned,
                                    num_data_points_returned, fragment_timestamps, fragment_counts,
                                    values):
        """
        Retrieve analog channel data
        
        Args:
            file_handle - file handle
            zero_based_channel_index - zero based channel index
            num_fragments_returned - ctypes.c_ulonglong class instance
            num_data_points_returned - ctypes.c_ulonglong class instance
            fragment_timestamps - ctypes.c_longlong class instance array the size of PL2AnalogChannelInfo.m_MaximumNumberOfFragments
            fragment_counts - ctypes.c_ulonglong class instance array the size of PL2AnalogChannelInfo.m_MaximumNumberOfFragments
            values - ctypes.c_short class instance array the size of PL2AnalogChannelInfo.m_NumberOfValues
            
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """


        self.pl2_dll.PL2_GetAnalogChannelData.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_short),
        )

        self.pl2_dll.PL2_GetAnalogChannelData.memsync = [
            {
                'p': [4],
                'l': [2],
                't': ctypes.c_longlong
            },
            {
                'p': [5],
                'l': [2],
                't': ctypes.c_ulonglong
            },
            {
                'p': [6],
                'l': [3],
                't': ctypes.c_short
            }
        ]

        result = self.pl2_dll.PL2_GetAnalogChannelData(self.file_handle,
                                                            ctypes.c_int(zero_based_channel_index),
                                                            num_fragments_returned,
                                                            num_data_points_returned,
                                                            fragment_timestamps,
                                                            fragment_counts,
                                                            values)

        return result

    def pl2_get_analog_channel_data_subset(self):
        pass

    def pl2_get_analog_channel_data_by_name(self, channel_name, num_fragments_returned,
                                            num_data_points_returned, fragment_timestamps,
                                            fragment_counts, values):
        """
        Retrieve analog channel data
        
        Args:
            file_handle - file handle
            channel_name - analog channel name
            num_fragments_returned - ctypes.c_ulonglong class instance
            num_data_points_returned - ctypes.c_ulonglong class instance
            fragment_timestamps - ctypes.c_longlong class instance array the size of PL2AnalogChannelInfo.m_MaximumNumberOfFragments
            fragment_counts - ctypes.c_ulonglong class instance array the size of PL2AnalogChannelInfo.m_MaximumNumberOfFragments
            values - ctypes.c_short class instance array the size of PL2AnalogChannelInfo.m_NumberOfValues
            
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetAnalogChannelDataByName.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_short),
        )

        self.pl2_dll.PL2_GetAnalogChannelDataByName.memsync = [
            {
                'p': [1],
                'n': True,  # null-terminated string flag
            },
            {
                'p': [4],
                'l': [2],
                't': ctypes.c_longlong
            },
            {
                'p': [5],
                'l': [2],
                't': ctypes.c_ulonglong
            },
            {
                'p': [6],
                'l': [3],
                't': ctypes.c_short
            }
        ]



        if hasattr(channel_name, 'encode'):
            channel_name = channel_name.encode('ascii')

        result = self.pl2_dll.PL2_GetAnalogChannelDataByName(
            self.file_handle,
            channel_name,
            num_fragments_returned,
            num_data_points_returned,
            fragment_timestamps,
            fragment_counts,
            values)

        return result

    def pl2_get_analog_channel_data_by_source(self, source_id, one_based_channel_index_in_source,
                                              num_fragments_returned, num_data_points_returned,
                                              fragment_timestamps, fragment_counts, values):
        """
        Retrieve analog channel data
        
        Args:
            file_handle - file handle
            source_id - numeric source ID
            one_based_channel_index_in_source - one-based channel index within the source
            num_fragments_returned - ctypes.c_ulonglong class instance
            num_data_points_returned - ctypes.c_ulonglong class instance
            fragment_timestamps - ctypes.c_longlong class instance array the size of PL2AnalogChannelInfo.m_MaximumNumberOfFragments
            fragment_counts - ctypes.c_ulonglong class instance array the size of PL2AnalogChannelInfo.m_MaximumNumberOfFragments
            values - ctypes.c_short class instance array the size of PL2AnalogChannelInfo.m_NumberOfValues
            
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetAnalogChannelDataBySource.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_short),
        )

        self.pl2_dll.PL2_GetAnalogChannelDataBySource.memsync = [
            {
                'p': [5],
                'l': [3],
                't': ctypes.c_longlong
            },
            {
                'p': [6],
                'l': [3],
                't': ctypes.c_ulonglong
            },
            {
                'p': [7],
                'l': [4],
                't': ctypes.c_short
            }
        ]

        result = self.pl2_dll.PL2_GetAnalogChannelDataBySource(self.file_handle,
                                                                    ctypes.c_int(source_id),
                                                                    ctypes.c_int(one_based_channel_index_in_source),
                                                                    num_fragments_returned,
                                                                    num_data_points_returned,
                                                                    fragment_timestamps,
                                                                    fragment_counts,
                                                                    values)

        return result

    def pl2_get_spike_channel_info(self, zero_based_channel_index, pl2_spike_channel_info):
        """
        Retrieve information about a spike channel
        
        Args:
            file_handle - file handle
            zero_based_channel_index - zero-based spike channel index
            pl2_spike_channel_info - PL2SpikeChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2SpikeChannelInfo passed to function is filled with channel info
        """

        self.pl2_dll.PL2_GetSpikeChannelInfo.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(PL2SpikeChannelInfo),
        )

        result = self.pl2_dll.PL2_GetSpikeChannelInfo(self.file_handle,
                                                           ctypes.c_int(zero_based_channel_index),
                                                           ctypes.byref(pl2_spike_channel_info))

        return result

    def pl2_get_spike_channel_info_by_name(self, channel_name, pl2_spike_channel_info):
        """
        Retrieve information about a spike channel
        
        Args:
            file_handle - file handle
            channel_name - spike channel name
            pl2_spike_channel_info - PL2SpikeChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2SpikeChannelInfo passed to function is filled with channel info
        """

        self.pl2_dll.PL2_GetSpikeChannelInfoByName.argtypes = (
            ctypes.c_int,
            ctypes.c_char * len(channel_name),
            ctypes.POINTER(PL2SpikeChannelInfo),
        )

        if hasattr(channel_name, 'encode'):
            channel_name = channel_name.encode('ascii')

        self.pl2_dll.PL2_GetSpikeChannelInfoByName.memsync = [
            {
                'p': [1],
                'n': True,  # null-terminated string flag
            }
        ]

        result = self.pl2_dll.PL2_GetSpikeChannelInfoByName(self.file_handle,
                                                                 channel_name,
                                                                 ctypes.byref(pl2_spike_channel_info))

        return result

    def pl2_get_spike_channel_info_by_source(self, source_id, one_based_channel_index_in_source,
                                             pl2_spike_channel_info):
        """
        Retrieve information about a spike channel
        
        Args:
            file_handle - file handle
            source_id - numeric source ID
            one_based_channel_index_in_source - one-based channel index within the source
            pl2_spike_channel_info - PL2SpikeChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2SpikeChannelInfo passed to function is filled with channel info
        """

        self.pl2_dll.PL2_GetSpikeChannelInfoBySource.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(PL2SpikeChannelInfo),
        )
        result = self.pl2_dll.PL2_GetSpikeChannelInfoBySource(
            self.file_handle,
            ctypes.c_int(source_id),
            ctypes.c_int(one_based_channel_index_in_source),
            ctypes.byref(pl2_spike_channel_info))

        return result

    def pl2_get_spike_channel_data(self, zero_based_channel_index, num_spikes_returned,
                                   spike_timestamps, units, values):
        """
        Retrieve spike channel data
        
        Args:
            file_handle - file handle
            zero_based_channel_index - zero based channel index
            num_spikes_returned - ctypes.c_ulonglong class instance
            spike_timestamps - ctypes.c_ulonglong class instance array the size of PL2SpikeChannelInfo.m_NumberOfSpikes
            units - ctypes.c_ushort class instance array the size of PL2SpikeChannelInfo.m_NumberOfSpikes
            values - ctypes.c_short class instance array the size of (PL2SpikeChannelInfo.m_NumberOfSpikes * PL2SpikeChannelInfo.m_SamplesPerSpike)
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        # extracting m_SamplesPerSpike to prepare data reading
        # This solution only works if all channels have the same number of samples per spike
        # as ctypes / zugbruecke is caching the memsync attribute once defined once
        spike_info = PL2SpikeChannelInfo()
        self.pl2_get_spike_channel_info(zero_based_channel_index, spike_info)
        samples_per_spike = spike_info.m_SamplesPerSpike

        self.pl2_dll.PL2_GetSpikeChannelData.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ushort),
            ctypes.POINTER(ctypes.c_short)
        )

        self.pl2_dll.PL2_GetSpikeChannelData.memsync = [
            {
                'p': [3],
                'l': [2],
                't': ctypes.c_longlong
            },
            {
                'p': [4],
                'l': [2],
                't': ctypes.c_ushort
            },
            {
                'p': [5],
                'l': ([2],),
                'func': f'lambda x: x.value * {samples_per_spike}',
                't': ctypes.c_short
            }
        ]

        result = self.pl2_dll.PL2_GetSpikeChannelData(self.file_handle,
                                                           ctypes.c_int(zero_based_channel_index),
                                                           num_spikes_returned,
                                                           spike_timestamps,
                                                           units,
                                                           values)

        return result

    def pl2_get_spike_channel_data_by_name(self, channel_name, num_spikes_returned,
                                           spike_timestamps, units, values):
        """
        Retrieve spike channel data
        
        Args:
            file_handle - file handle
            channel_name = channel name
            num_spikes_returned - ctypes.c_ulonglong class instance
            spike_timestamps - ctypes.c_ulonglong class instance array the size of PL2SpikeChannelInfo.m_NumberOfSpikes
            units - ctypes.c_ushort class instance array the size of PL2SpikeChannelInfo.m_NumberOfSpikes
            values - ctypes.c_short class instance array the size of (PL2SpikeChannelInfo.m_NumberOfSpikes * PL2SpikeChannelInfo.m_SamplesPerSpike)
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetSpikeChannelDataByName.argtypes = (
            ctypes.c_int,
            ctypes.c_char,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong * len(spike_timestamps)),
            ctypes.POINTER(ctypes.c_ushort * len(units)),
            ctypes.POINTER(ctypes.c_short * len(values))
        )

        # extracting m_SamplesPerSpike to prepare data reading
        # This solution only works if all channels have the same number of samples per spike
        # as ctypes / zugbruecke is caching the memsync attribute once defined once
        spike_info = PL2SpikeChannelInfo()
        self.pl2_get_spike_channel_info_by_name(channel_name, spike_info)
        samples_per_spike = spike_info.m_SamplesPerSpike

        self.pl2_dll.PL2_GetSpikeChannelDataByName.memsync = [
            {
                'p': [1],
                'n': True,  # null-terminated string flag
            },
            {
                'p': [3],
                'l': [2],
                't': ctypes.c_longlong
            },
            {
                'p': [4],
                'l': [2],
                't': ctypes.c_ushort
            },
            {
                'p': [5],
                'l': ([2],),
                'func': f'lambda x: x.value * {samples_per_spike}',
                't': ctypes.c_short
            }
        ]

        if hasattr(channel_name, 'encode'):
            channel_name = channel_name.encode('ascii')

        result = self.pl2_dll.PL2_GetSpikeChannelDataByName(self.file_handle,
                                                                 channel_name,
                                                                 num_spikes_returned,
                                                                 spike_timestamps,
                                                                 units,
                                                                 values)

        return result

    def pl2_get_spike_channel_data_by_source(self, source_id, one_based_channel_index_in_source,
                                             num_spikes_returned, spike_timestamps, units, values):
        """
        Retrieve spike channel data
        
        Args:
            file_handle - file handle
            source_id - numeric source ID
            one_based_channel_index_in_source - one-based channel index within the source
            num_spikes_returned - ctypes.c_ulonglong class instance
            spike_timestamps - ctypes.c_ulonglong class instance array the size of PL2SpikeChannelInfo.m_NumberOfSpikes
            units - ctypes.c_ushort class instance array the size of PL2SpikeChannelInfo.m_NumberOfSpikes
            values - ctypes.c_short class instance array the size of (PL2SpikeChannelInfo.m_NumberOfSpikes * PL2SpikeChannelInfo.m_SamplesPerSpike)
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetSpikeChannelDataBySource.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_ushort),
            ctypes.POINTER(ctypes.c_short),
        )

        # extracting m_SamplesPerSpike to prepare data reading
        # This solution only works if all channels have the same number of samples per spike
        # as ctypes / zugbruecke is caching the memsync attribute once defined once
        spike_info = PL2SpikeChannelInfo()
        self.pl2_get_spike_channel_info_by_source(source_id, one_based_channel_index_in_source, spike_info)
        samples_per_spike = spike_info.m_SamplesPerSpike

        self.pl2_dll.PL2_GetSpikeChannelDataBySource.memsync = [
            {
                'p': [4],
                'l': [3],
                't': ctypes.c_longlong
            },
            {
                'p': [5],
                'l': [3],
                't': ctypes.c_ushort
            },
            {
                'p': [6],
                'l': ([3],),
                'func': f'lambda x: x.value * {samples_per_spike}',
                't': ctypes.c_short
            }
        ]

        result = self.pl2_dll.PL2_GetSpikeChannelDataBySource(self.file_handle,
                                                                   ctypes.c_int(source_id),
                                                                   ctypes.c_int(one_based_channel_index_in_source),
                                                                   num_spikes_returned,
                                                                   spike_timestamps,
                                                                   units,
                                                                   values)

        return result

    def pl2_get_digital_channel_info(self, zero_based_channel_index, pl2_digital_channel_info):
        """
        Retrieve information about a digital event channel
        
        Args:
            file_handle - file handle
            zero_based_channel_index - zero-based digital event channel index
            pl2_digital_channel_info - PL2DigitalChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2DigitalChannelInfo passed to function is filled with channel info
        """

        self.pl2_dll.PL2_GetDigitalChannelInfo.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(PL2DigitalChannelInfo),
        )

        result = self.pl2_dll.PL2_GetDigitalChannelInfo(
            self.file_handle,
            ctypes.c_int(zero_based_channel_index),
            ctypes.byref(pl2_digital_channel_info)
        )

        return result

    def pl2_get_digital_channel_info_by_name(self, channel_name, pl2_digital_channel_info):
        """
        Retrieve information about a digital event channel
        
        Args:
            file_handle - file handle
            channel_name - digital event channel name
            pl2_digital_channel_info - PL2DigitalChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2DigitalChannelInfo passed to function is filled with channel info
        """

        if hasattr(channel_name, 'encode'):
            channel_name = channel_name.encode('ascii')

        self.pl2_dll.PL2_GetDigitalChannelInfoByName.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char),
            ctypes.POINTER(PL2DigitalChannelInfo),
        )

        self.pl2_dll.PL2_GetDigitalChannelInfoByName.memsync = [
            {
                'p': [1],  # ctypes.POINTER argument
                'n': True,  # null-terminated string flag
            }
        ]
        result = self.pl2_dll.PL2_GetDigitalChannelInfoByName(
            self.file_handle,
            channel_name,
            ctypes.byref(pl2_digital_channel_info)
        )

        return result

    def pl2_get_digital_channel_info_by_source(self, source_id, one_based_channel_index_in_source,
                                               pl2_digital_channel_info):
        """
        Retrieve information about a digital event channel
        
        Args:
            file_handle - file handle
            source_id - numeric source ID
            one_based_channel_index_in_source - one-based channel index within the source
            pl2_digital_channel_info - PL2DigitalChannelInfo class instance
        
        Returns:
            1 - Success
            0 - Failure
            The instance of PL2DigitalChannelInfo passed to function is filled with channel info
        """

        self.pl2_dll.PL2_GetDigitalChannelInfoBySource.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(PL2DigitalChannelInfo),
        )
        result = self.pl2_dll.PL2_GetDigitalChannelInfoBySource(
            self.file_handle,
            ctypes.c_int(source_id),
            ctypes.c_int(one_based_channel_index_in_source),
            ctypes.byref(pl2_digital_channel_info)
        )

        return result

    def pl2_get_digital_channel_data(self, zero_based_channel_index, num_events_returned,
                                     event_timestamps, event_values):
        """
        Retrieve digital even channel data
        
        Args:
            file_handle - file handle
            zero_based_channel_index - zero-based digital event channel index
            num_events_returned - ctypes.c_ulonglong class instance
            event_timestamps - ctypes.c_longlong class instance array the size of PL2DigitalChannelInfo.m_NumberOfEvents
            event_values - ctypes.c_ushort class instance array the size of PL2DigitalChannelInfo.m_NumberOfEvents
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetDigitalChannelData.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_short),
        )

        self.pl2_dll.PL2_GetDigitalChannelData.memsync = [
            {
                'p': [3],
                'l': [2],
                't': ctypes.c_longlong
            },
            {
                'p': [4],
                'l': [2],
                't': ctypes.c_ushort
            },
        ]

        result = self.pl2_dll.PL2_GetDigitalChannelData(
            self.file_handle,
            ctypes.c_int(zero_based_channel_index),
            num_events_returned,
            event_timestamps,
            event_values)

        return result

    def pl2_get_digital_channel_data_by_name(self, channel_name, num_events_returned,
                                             event_timestamps, event_values):
        """
        Retrieve digital even channel data
        
        Args:
            file_handle - file handle
            channel_name - digital event channel name
            num_events_returned - ctypes.c_ulonglong class instance
            event_timestamps - ctypes.c_longlong class instance array the size of PL2DigitalChannelInfo.m_NumberOfEvents
            event_values - ctypes.c_ushort class instance array the size of PL2DigitalChannelInfo.m_NumberOfEvents
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        if hasattr(channel_name, 'encode'):
            channel_name = channel_name.encode('ascii')

        self.pl2_dll.PL2_GetDigitalChannelDataByName.argtypes = (
            ctypes.c_int,  # file handle
            ctypes.POINTER(ctypes.c_char),  # channel name
            ctypes.POINTER(ctypes.c_ulonglong),  # equivalent to m_NumberOfEvents
            ctypes.POINTER(ctypes.c_longlong),  # array of timestamps of length m_NumberOfEvents
            ctypes.POINTER(ctypes.c_ushort),  # array of values m_NumberOfEvents
        )

        self.pl2_dll.PL2_GetDigitalChannelDataByName.memsync = [
            {
                'p': [1],  # ctypes.POINTER argument
                'n': True,  # null-terminated string flag
            },
            {
                'p': [3],
                'l': [2],
                't': ctypes.c_longlong
            },
            {
                'p': [4],
                'l': [2],
                't': ctypes.c_ushort
            }
        ]
        result = self.pl2_dll.PL2_GetDigitalChannelDataByName(self.file_handle,
                                                                   channel_name,
                                                                   num_events_returned,
                                                                   event_timestamps,
                                                                   event_values)

        return result

    def pl2_get_digital_channel_data_by_source(self, source_id, one_based_channel_index_in_source,
                                               num_events_returned, event_timestamps,
                                               event_values):
        """
        Retrieve digital even channel data
        
        Args:
            file_handle - file handle
            source_id - numeric source ID
            one_based_channel_index_in_source - one-based channel index within the source
            num_events_returned - ctypes.c_ulonglong class instance
            event_timestamps - ctypes.c_longlong class instance array the size of PL2DigitalChannelInfo.m_NumberOfEvents
            event_values - ctypes.c_ushort class instance array the size of PL2DigitalChannelInfo.m_NumberOfEvents
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetDigitalChannelDataBySource.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_ushort),
        )

        self.pl2_dll.PL2_GetDigitalChannelDataBySource.memsync = [
            {
                'p': [4],
                'l': [3],
                't': ctypes.c_longlong
            },
            {
                'p': [5],
                'l': [3],
                't': ctypes.c_ushort
            }
        ]

        result = self.pl2_dll.PL2_GetDigitalChannelDataBySource(
            self.file_handle,
            ctypes.c_int(source_id),
            ctypes.c_int(one_based_channel_index_in_source),
            num_events_returned,
            event_timestamps,
            event_values)

        return result

    def pl2_get_start_stop_channel_info(self, number_of_start_stop_events):
        """
        Retrieve information about start/stop channel
        
        Args:
            file_handle - file handle
            number_of_start_stop_events - ctypes.c_ulonglong class instance
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetStartStopChannelInfo.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong)
        )

        result = self.pl2_dll.PL2_GetStartStopChannelInfo(
            self.file_handle,
            number_of_start_stop_events
        )

        return result

    def pl2_get_start_stop_channel_data(self, num_events_returned, event_timestamps, event_values):
        """
        Retrieve digital channel data
        
        Args:
            file_handle - file handle
            num_events_returned - ctypes.c_ulonglong class instance
            event_timestamps - ctypes.c_longlong class instance
            event_values - point to ctypes.c_ushort class instance
        
        Returns:
            1 - Success
            0 - Failure
            The class instances passed to the function are filled with values
        """

        self.pl2_dll.PL2_GetStartStopChannelInfo.argtypes = (
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_ushort)
        )

        self.pl2_dll.PL2_GetStartStopChannelInfo.memsync = [
            {
                'p': [2],
                'l': [1],
                't': ctypes.c_longlong
            },
            {
                'p': [3],
                'l': [1],
                't': ctypes.c_ushort
            },
        ]

        result = self.pl2_dll.PL2_GetStartStopChannelData(self.file_handle,
                                                               num_events_returned,
                                                               event_timestamps,
                                                               event_values)

        return result

    # PL2 data block functions purposefully not implemented.
    def pl2_read_first_data_block(self):
        pass

    def pl2_read_next_data_block(self):
        pass

    def pl2_get_data_block_info(self):
        pass

    def pl2_get_data_block_timestamps(self):
        pass

    def pl2_get_spike_data_block_units(self):
        pass

    def pl2_get_spike_data_block_waveforms(self):
        pass

    def pl2_get_analog_data_block_timestamp(self):
        pass

    def pl2_get_analog_data_block_values(self):
        pass

    def pl2_get_digital_data_block_timestamps(self):
        pass

    def pl2_get_start_stop_data_block_timestamps(self):
        pass

    def pl2_get_start_stop_data_block_values(self):
        pass
